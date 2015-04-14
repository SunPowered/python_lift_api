""" main.py - The main loop and command caller """
import sys
import inspect
import time

import plan as plans
import strategy as strategies
from controller import Controller
from boxlift_api import BoxLift, PYCON2015_EVENT_NAME
from config import Config as cfg


def print_commands(commands):
    print "--- Commands ---"
    for command in commands:
        print command


def print_loop_counter(cnt, n_iter):
    print_every = 2
    print
    if cnt % print_every == 0:
        print "Iteration {}/{}".format(cnt, n_iter)


def print_simulation_header(plan, options):
    print "Starting Boxlift Sim"
    print "Using plan: {}".format(plan.name)
    print "Using strategy: {}".format(plan.strategy.name())
    print "Options: {}".format(options)
    print "---"


def print_simulation_results(resp):
    print "--- Sim Finished ---"
    print "Score: {}".format(resp.get('score', None))
    event_code = resp.get('event_code', None)
    if event_code is not None:
        print "Holy Crap!  You won something!  Event code: {}".format(event_code)


def send_commands(api, commands):
    n_retry = 3
    resp = api.send_commands(commands)
    success = False
    while not success and n_retry > 0:
        if resp['status'] == 'error':
            print "API Error: {}".format(resp['message'])
            print "retrying: {}".format(n_retry)
            time.sleep(1)
            n_retry -= 1
        else:
            success = True
    if not success:
        print "API Retry Exhausted.  I'm dying!"
        sys.exit(1)
    return resp


def main(options):
    # check the plan argument
    plan = None
    for clsname, clsobj in inspect.getmembers(plans):
        if clsname == options.plan:
            plan = clsobj
            break
    if plan is None:
        raise TypeError("No plan exists for name: {}".format(options.plan))

    # Check the strategy argument
    if options.strategy is not None:
        for clsname, clsobj in inspect.getmembers(strategies):
            if clsname == options.strategy:
                plan.strategy = clsobj

    api_verbose = options.verbose == 2

    print_simulation_header(plan, options)

    controller = Controller(plan, debug=options.verbose > 0)
    # api = BoxLift(cfg.username, plan.name, cfg.email, cfg.registration_id,
    #               event_name=PYCON2015_EVENT_NAME, sandbox_mode=options.sandbox,
    #               verbose=api_verbose)
    api = BoxLift(cfg.username, plan.name, cfg.email, sandbox_mode=options.sandbox,
                  verbose=api_verbose)
    resp = send_commands(api, [])
    controller.update(resp)
    commands = controller.get_commands()
    # The loop
    loop_counter = 0

    while 1:
        loop_counter += 1
        print_loop_counter(loop_counter, plan.n_iter)

        if options.verbose:
            controller.print_status()
            print_commands(commands)

        if options.debug:

            uinput = raw_input('''\n--- Continue ---\n''')
            if uinput == 'd':
                import pdb; pdb.set_trace()

        resp = send_commands(api, commands)

        if resp.get('status', '') == 'finished':
            print_simulation_results(resp)
            break

        controller.update(resp)
        controller.shuffle_requests()
        commands = controller.get_commands()
        time.sleep(0.25)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Codelift Challenge - SunPowered')
    parser.add_argument('-d', '--debug', action='store_true', default=False, 
                        help='Enables debug mode, stops after each step')
    parser.add_argument('-v', '--verbose', action='count', default=False,
                        help='Enables API verbosity, logging API requests and responses')
    parser.add_argument('plan', default='Training1', help='The plan to use for the simulation')
    parser.add_argument('-s', '--sandbox', action='store_true', default=False,
                        help='Enable sandbox mode.  Auto enabled with debug option')
    parser.add_argument('-t', '--strategy', default=None, 
                        help='Provide a strategy to the elevators, this will override any\
 strategy existing in the building plan')
    options = parser.parse_args()

    if options.debug:
        options.sandbox = True

    main(options)

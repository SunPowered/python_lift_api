""" main.py - The main loop and command caller """
import inspect
import time

import plan as plans
from controller import Controller
from boxlift_api import BoxLift, PYCON2015_EVENT_NAME
from config import Config as cfg


def print_commands(commands):
    print "--- Commands ---"
    for command in commands:
        print command


def print_loop_counter(cnt, n_iter):
    print_every = 5
    if cnt % print_every == 0:
        print "Iteration {}/{}".format(cnt, n_iter)


def print_simulation_header(plan, options):
    print "Starting Boxlift Sim"
    print "Using plan: {}".format(plan.name)
    print "Options: {}".format(options)
    print "---"


def print_simulation_results(resp):
    print "--- Sim Finished ---"
    print "Score: {}".format(resp.get('score', None))
    event_code = resp.get('event_code', None)
    if event_code is not None:
        print "Holy Crap!  You won something!  Event code: {}".format(event_code)


def main(options):
    # check the plan argument
    plan = None
    for clsname, clsobj in inspect.getmembers(plans):
        if clsname == options.plan:
            plan = clsobj
    if plan is None:
        raise TypeError("No plan exists for name: {}".format(options.plan))

    api_verbose = options.verbose == 2

    print_simulation_header(plan, options)

    controller = Controller(plan)
    api = BoxLift(cfg.username, plan.name, cfg.email, cfg.registration_id,
                  event_name=PYCON2015_EVENT_NAME, sandbox_mode=options.sandbox,
                  verbose=api_verbose)

    resp = api.send_commands([])
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

        resp = api.send_commands(commands)

        if resp.get('status', '') == 'finished':
            print_simulation_results(resp)
            break

        controller.update(resp)
        commands = controller.get_commands()
        time.sleep(0.25)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='boxlift program - TvB')
    parser.add_argument('-d', '--debug', action='store_true', default=False, 
                        help='Enables debug mode, stops after each step')
    parser.add_argument('-v', '--verbose', action='count', default=False,
                        help='Enables API verbosity, logging API requests and responses')
    parser.add_argument('plan', default='Training1', help='The plan to use for the simulation')
    parser.add_argument('-s', '--sandbox', action='store_true', default=False,
                        help='Enable sandbox mode.  Auto enabled with debug option')

    options = parser.parse_args()

    if options.debug:
        options.sandbox = True

    main(options)

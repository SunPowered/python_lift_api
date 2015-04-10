""" Run the script """
import random
import time

from config import Config
from boxlift_api import PYCON2015_EVENT_NAME, Command, BoxLift


class TrainingPlan(object):
    name = 'training_1'
    floors = 10
    n_el = 2
    steps = 30

MAX_LOOPS = 2000


class LoopIterationError(Exception):
    def __init__(self):
        msg = "Max loop iteraion of {} hit.  Failing out".format(MAX_LOOPS)
        super(LoopIterationError, self).__init__(msg)


class Go(object):
    def __init__(self, plan, sandbox_mode=False, verbose_api=False, debug=False):
        self.plan = plan
        self.bl = BoxLift(Config.username, self.plan.name, Config.email,
                          Config.registration_id, event_name=PYCON2015_EVENT_NAME,
                          sandbox_mode=sandbox_mode, verbose=verbose_api)

        self.debug = debug
        self.state = None
        self.els = {}
        self.requests = {}
        self.init_els()
        self.init_commands()
        self.counter = 0

    def init_commands(self):
        """ Initial command set """
        commands = []
        # send half of elevators to top floor
        # commands.extend(self._send_half_up())
        self.send_commands(commands)

    def init_els(self):
        for el in range(self.plan.n_el):
            self.els[el] = {'prev_floor': 0,
                            'accepted_requests': []}

    def assign_request(self, el, floor):
        if self.is_request_assigned(floor) is False:
            ars = self.els[el]['accepted_requests']
            if floor not in ars:
                ars.append(floor)

    def deassign_request(self, el, floor):
        if self.is_request_assigned(floor) == el:
            self.els[el]['accepted_requests'].remove(floor)

    def is_request_assigned(self, floor):
        for el in self.els:
            if floor in self.els[el]['accepted_requests']:
                return el
        return False

    def _elevator_data(self, el):
        """ Elevator Data """
        for els in self.state['elevators']:
            if els['id'] == el:
                return els

    def el_direction(self, el):
        """ Elevator direction """
        el_state = self._elevator_data(el)
        prev_floor = self.els[el]['prev_floor']
        floor_diff = int(el_state['floor']) - prev_floor
        try:
            floor_diff / abs(floor_diff)
        except ZeroDivisionError:
            return 0

    def sample_els(self):
        """ Random ordering of els"""
        return random.sample(range(self.plan.n_el), self.plan.n_el)

    def direction_requests(self, direction):
        """ Returns the floors requesting a particular direction """
        return [r['floor'] for r in self.state['requests'] if r['direction'] == direction]

    def get_sign(self, num):
        if num == 0:
            return 0
        return int(num) / abs(num)

    def _send_half_up(self):
        all_els = self.sample_els()
        els = all_els[:len(all_els) / 2]
        commands = []
        for el in els:
            commands.append(Command(el, direction=1, speed=1))
        return commands

    def send_commands(self, commands):
        """ Send a set of commands and save the present state to work with """
        self.state = self.bl.send_commands(commands)
        self.post_process_state()

    def post_process_state(self):
        """ Process the important data so we don't have to keep parsing things
            over and over. """
        if self.state:
            self.requests = self.process_requests()
            self.process_els()

    def _post_simulation(self):
        """Get some stats of the sim including score and maybe some other things"""
        res_str = ""
        score = self.state.get('score', None)
        if score:
            res_str += "Score: {}".format(score)
        event_code = self.state.get('event_code', None)
        if event_code:
            res_str += "\nHoly shit! You won something.  Event Code: {}".format(event_code)

        return res_str

    def process_els(self):
        """ Save some data about the last state of the els """
        for el in self.state.get('elevators', []):
            self.els[el['id']]['prev_floor'] = el['floor']

    def process_requests(self):
        """ Split the requests by direction, return the floors"""

        up_ = []
        down_ = []

        for req in self.state['requests']:
            if req['direction'] == -1:
                down_.append(req['floor'])
            elif req['direction'] == 1:
                up_.append(req['floor'])
        all_ = up_
        all_.extend(down_)

        return {'1': tuple(up_), '-1': tuple(down_), 'all': tuple(set(all_))}

    def get_commands(self):
        """ The main logic controller """
        commands = []

        for el in self.sample_els():
            # Check which els should stop
            if self.should_el_stop(el):
                commands.append(Command(el, speed=0))

            # Next determine which els need to move
            motion = self.should_el_move(el)
            if motion != self.el_direction(el):
                commands.append(Command(el, speed=1, direction=motion))
        return commands

    def print_status(self):
        """ Print the current status of els, buttons, and requests """
        els = self.state['elevators']
        requests = self.requests
        print " -- Step Status -- "
        for el in els:
            print "Elevator {} - Floor: {}  Buttons: {} Requests: {}".format(el['id'], 
                                                                             el['floor'], 
                                                                             el['buttons_pressed'],
                                                                             self.els[el['id']]['accepted_requests'])
        print "Down Requests: {}".format(requests.get(-1, []))
        print "Up Requests: {}".format(requests.get(1, []))

    def print_commands(self, commands):
        print " -- Commands Issued --"
        for command in commands:
            print command

    def should_el_stop(self, el):
        """ Check whether elevators should stop.  This occurs when
        it is in motion and hits a floor that is either requested
        from within, if there is a request in its direction of travel,
        or when a request is at an extreme top/bottom """

        el_state = self._elevator_data(el)
        el_dir = self.el_direction(el)

        # If its already stopped, return early
        if el_dir == 0:
            return False

        # If it hits a floor that is being requested by its buttons, then stop
        if el_state['floor'] in el_state['buttons_pressed']:
            return True

        if self.is_floor_assigned(el_state['floor']):
            self.deassign_request(el, el_state['floor'])
            return True

        # floor_reqs = self.requests[el_dir]
        # all_reqs = self.requests['all']

        # # If a floor is requested in its direction of travel, then stop and pick them up!
        # if el_state['floor'] in floor_reqs:
        #     return True

        # # If there are no button requests, and the current floor has a request in any
        # # direction, then stop and pick them up.
        # if len(el_state['buttons_pressed'] == 0) and el_state['floor'] in all_reqs:
        #     return True

        return False

    def should_el_move(self, el):
        """ 1. If an el is moving and there are requested buttons or requests in its direction, then
            keep on keepin' on.

            2. If an el is stopped and there are buttons pressed in any direction, go that way.

            3. If an el is stopped and there are no buttons pressed, go to the nearest request

            4. If an el is stopped and there are no button or requests, then go home (1)

            5. If an el is stopped and home, then stay put.

            Returns direction el should be moving """

        el_status = self._elevator_data(el)
        el_dir = self.el_direction(el)

        # 1.
        if el_dir != 0 and len(el_status['buttons_pressed']) != 0:
            return 0

        if el_dir == 0:
            # 2.
            if len(el_status['buttons_pressed']) != 0:
                return self.get_sign(el_status['buttons_pressed'][0] - el_status['floor'])

            # 3.
            if len(self.requests['all']) > 0:
                for i in self.requests['all']:
                    if not self.is_request_assigned(i):
                        self.assign_request(el, i)

                        if self.el_direction(el) != 0:
                            return 0
                        else:
                            return self.get_sign(self.requests['all'][0] - el_status['floor'])

            # 4.
            if el_status['floor'] != 0:
                return -1
            else:
                # 5.
                return 0

    def loop(self):
        print "Starting Loop"
        if not self.state:
            self.send_commands()
        while self.state['status'] != 'finished':
            self.counter += 1
            print "Step {}/{}".format(self.counter, self.plan.steps)

            commands = self.get_commands()
            if self.debug:
                self.print_status()
                self.print_commands(commands)
            self.send_commands(commands)

            if self.counter > MAX_LOOPS:
                raise LoopIterationError()

            if self.debug:
                # Get user input to go on
                v = raw_input("Continue...")
                if v == 'd':
                    # Drop to pdb
                    import pdb
                    pdb.set_trace()
            else:
                time.sleep(0.5)

        print "Finished!"
        print self._post_simulation()


if __name__ == '__main__':
    print "Starting"
    sandbox = True
    verbose = True
    debug = False
    go = Go(TrainingPlan(), sandbox_mode=sandbox, debug=debug)
    go.loop()

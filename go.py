""" Run the script """
import random
import time

from config import Config
from boxlift_api import PYCON2015_EVENT_NAME, Command, BoxLift


class Plan(object):
    name = 'training_1'
    floors = 10
    n_el = 2


class Go(object):
    def __init__(self, plan, sandbox_mode=False, verbose=False):
        self.plan = plan
        self.bl = BoxLift(Config.username, self.plan.name, Config.email,
                          Config.registration_id, event_name=PYCON2015_EVENT_NAME,
                          sandbox_mode=sandbox_mode, verbose=verbose)

        self.state = None
        self.init_commands()

    def init_commands(self):
        """ Initial command set"""
        commands = []
        # send half of elevators to top floor
        commands.append(self._send_half_up())
        self.send_commands(commands)

    def iter_els(self):
        for el in range(self.plan.n_el):
            yield el

    def _send_half_up(self):
        els = random.sample(self.iter_els, self.plan.n_el / 2)
        commands = []
        for el in els:
            commands.append(Command(el, direction=1, speed=1))
        return commands

    def send_commands(self, commands):
        self.state = self.bl.send_commands(commands)

    def loop(self):
        print "Starting Loop"
        while self.state.status != 'finished':
            commands = self.get_commands()
            self.send_commands(commands)
            time.sleep(1)

        print "Finished!"

    def get_commands(self):
        """ The main logic controller """
        commands = []

        for el in self.iter_els():
            # Check which els should stop
            if self.should_el_stop(el):
                commands.append(Command(el, speed=0))

            # Next determine which els need to move
            motion = self.should_el_move(el)
            if motion is not False:
                commands.append(Command(el, speed=1, direction=motion))
        return commands

    def _elevator_data(self, el):
        for els in self.state['elevators'].iteritems():
            if els['id'] == el:
                return els

    def _is_floor_requested(self, floor, direction=None):
        for request in self.state['requests']:
            if floor == request['floor']:
                if direction is None or direction == request['direction']:
                    return True
        return False

    def _floor_requests(self):
        return [req['floor'] for req in self.state['requests']]

    def should_el_stop(self, el):
        """ Check whether elevators should stop.  This occurs when
        it is in motion and hits a floor that is either requested
        from within, if there is a request in its direction of travel,
        or when a request is at an extreme top/bottom """

        el_state = self._elevator_data(el)
        if el_state['speed'] == 0:
            return False
        if el_state['floor'] in el_state['buttons_pressed']:
            return True
        floor_reqs = self._floor_requests()
        if el_state['floor'] in (max(floor_reqs), min(floor_reqs)):
            return True
        if self._is_floor_requested(el_state['floor'], direction=el_state['direction']):
            return True

        return False

    def should_el_move(self, el):
        """"""
        pass

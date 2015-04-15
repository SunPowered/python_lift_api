""" controller.py - A general elevator controller """
import random

from elevator import Elevator
from plan import BasePlan


class Controller(object):
    """ Base controller object.  Handles the logic for assigning requests and issuing commands """

    def __init__(self, plan, debug=False):
        """ Takes a plan object ref and other kwargs to pass to the BoxLift API. """

        if not issubclass(plan, BasePlan) and not isinstance(plan, BasePlan):
            raise TypeError("plan argument must be a subclass of BasePlan")
        self.plan = plan
        self.elevators = []
        self.debug = debug
        self.init_elevators(debug=self.debug)

    def init_elevators(self, **kwargs):
        self.elevators = []
        for idx in range(self.plan.n_els):
            self.elevators.append(Elevator(idx, self.plan.n_floors, **kwargs))
        self.plan.strategy.init_elevators(self.elevators)
        if self.debug:
            self.print_elevators_info()

    def print_elevators_info(self):
        for el in self.elevators:
            el.print_info()

    def is_request_assigned(self, req):
        """ Check all elevators whether the request is assigned """
        return any([el.is_request_assigned(*req) for el in self.elevators])
        # for el in self.elevators:
        #     if el.is_request_assigned(*req):
        #         return True
        # return False

    def assign_request(self, req):
        """ Assign a request to one of the current elevators.  There are some rules
        to abide by when selecting what elevator to assign the request to:

        -  Find the closest elevator who is already on its way to the request
        -  If not directly on the way, try to balance the request load between elevators
        """

        if self.is_request_assigned(req):
            return

        # Check whether request is on the way to an elevator
        
        #elevator = self.find_elevator_by_req_otw(req)

        elevator = self.find_elevator_by_req_metric(req)
        self.elevators[elevator].assign_request(*req)
        return
        
        # if elevator is not None:
        #     # Assign it to this elevator
        #     self.elevators[elevator].assign_request(*req)
        #     return

        # # Find the minimum of distance*n_reqs**2 for the elevator stack
        # elevator = self.find_elevator_by_req_metric(req)
        # self.elevators[elevator].assign_request(*req)

    def find_elevator_by_req_otw(self, req):
        """  Check and see whether the request is already on the way of
             an elevator.  If multiple yesses, choose closest one.  If none,
             return None.
        """
        req_floor, requests_dir = req
        els = []

        # Find closest elevator that is on the way
        distances = [(el, el.distance_to(req_floor)) for el in self.elevators]
        distances.sort(key=lambda x: x[1])
        for el in zip(*distances)[0]:
            # If the elevator is stopped, then send it up
            # If the request is on the way, we're ok
            if not el.has_any_requests() or (el.direction_to(req_floor) == el.direction):
                return el.id_

        return None

    def find_elevator_by_req_metric(self, req):
        """ Get the minimum of a request metric to determine which
            elevator to select
        """
        metrics = []
        for el in self.elevators:
            metrics.append((el.id_, self.plan.strategy.distance_metric(el, req)))

        # Sort and get the minimum value
        metrics.sort(key=lambda x: x[1])
        return metrics[0][0]

    def print_status(self):
        """ Print the current elevator status """
        print """ --- Status --- """
        for el in self.elevators:
            print el

    def update(self, resp):
        """ Update the elevators, assign the requests """

        # Update the elevator state
        els = resp.get("elevators", None)
        if els is not None:
            for el in els:
                self.elevators[el.get('id')].update_state(el)

        # Assign all requests
        reqs = resp.get("requests", None)
        if reqs is not None:
            for req in reqs:
                # wrap request
                req = (req['floor'], req['direction'])
                self.assign_request(req)

    def get_commands(self):
        """ Get the commands from all elevators """
        commands = []
        for el in self.elevators:
            command = el.get_command()
            if command is not None:
                commands.append(command)
        return commands

    def shuffle_requests(self):
        """ Find requests that are in the opposite direction of 
            travel, and try to reassign them to a closer or stopped
            elevator. """

        opposing_requests = self.find_opposing_requests()

        for req, cur_el in opposing_requests:
            cur_elevator = self.elevators[cur_el]
            # Find closest elevator that is not moving away
            el = self.find_closest_el_not_moving_away(req)
            if el is not None:
                if self.debug:
                    print "Shuffling req {} from el {} to {}".format(req, cur_el, el)
                # import pdb; pdb.set_trace()
                elevator = self.elevators[el]
                cur_elevator.remove_request(*req)
                elevator.assign_request(*req)

    def find_opposing_requests(self):
        """ Get the opposing requests """
        reqs = []
        for el in self.elevators:
            for req in el.requests:
                dir_to_req = el.direction_to(req[0])
                if dir_to_req in [0, el.direction] or el.direction == 0:
                    continue
                else:
                    reqs.append((req, el.id_))
        return reqs

    def find_closest_el_not_moving_away(self, req):
        """ Find the closest elevator not moving away from a request"""
        all_els = []
        for el in random.sample(self.elevators, len(self.elevators)):
            if el.direction == 0 or el.direction_to(req[0]) == el.direction:
                all_els.append((el.id_, el.distance_to(req[0])))
        all_els.sort(key=lambda x: x[1])
        if not all_els:
            return None
        return all_els[0][0]

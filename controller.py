""" controller.py - A general elevator controller """

from elevator import Elevator
from plan import BasePlan


class Controller(object):
    """ Base controller object.  Handles the logic for assigning requests and issuing commands """

    def __init__(self, plan, **kwargs):
        """ Takes a plan object ref and other kwargs to pass to the BoxLift API. """

        if not issubclass(plan, BasePlan) and not isinstance(plan, BasePlan):
            raise TypeError("plan argument must be a subclass of BasePlan")
        self.plan = plan
        self.elevators = []
        self.init_elevators()

    def init_elevators(self):
        self.elevators = []
        for idx in range(self.plan.n_els):
            self.elevators.append(Elevator(idx))

    def assign_request(self, req):
        """ Assign a request to one of the current elevators.  There are some rules
        to abide by when selecting what elevator to assign the request to:

        -  Find the closest elevator who is already on its way to the request
        -  If not directly on the way, try to balance the request load between elevators
        """

        # Check whether request is on the way to another elevator
        elevator = self.find_elevator_by_req_otw(req)

        if elevator is not None:
            # Assign it to this elevator
            self.elevators[elevator].assign_request(req)
            return

        # Find the minimum of distance*n_reqs**2 for the elevator stack
        elevator = self.find_elevator_by_req_metric(req)
        self.elevators[elevator].assign_request(req)

    def find_elevator_by_req_otw(self, req):
        """  Check and see whether the request is already on the way of
             an elevator.  If multiple yesses, choose closest one.  If none,
             return None.
        """
        req_floor, requests_dir = req
        els = []
        for el in self.elevators:
            if not el.has_buttons():
                continue
            if el.direction_to(req_floor) == el.direction:
                distance = el.distance_to(req_floor)
                els.append((el.id_, distance))

        el_len = len(els)
        if el_len == 0:
            return None
        elif el_len == 1:
            return els[0][0]
        else:
            # Find shortest distance
            return sorted(els, key=lambda x: x[1])[0][0]

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
                self.elevators[el.id_].update_state(el)

        # Assign all requests
        reqs = resp.get("requests", None)
        if reqs is not None:
            for req in reqs:
                self.assign_request(req)

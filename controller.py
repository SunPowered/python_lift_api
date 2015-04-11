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
        for idx in range(self.plan.n_els):
            self.elevators.append(Elevator(idx))


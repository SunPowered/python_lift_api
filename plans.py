""" A simple file to store the various building plans """


class BasePlan(object):
    name = None  # The plan name
    n_els = 2    # The number of elevators
    n_iter = 30  # The number of iterations


class Training1(BasePlan):
    name = "training_1"

""" A simple file to store the various building plans """


class BasePlan(object):
    name = None    # The plan name
    n_els = 2      # The number of elevators
    n_iter = 30    # The number of iterations
    n_floors = 10  # The number of floors


class Training1(BasePlan):
    name = "training_1"


class Training2(BasePlan):
    name = "training_2"
    n_els = 4
    n_iter = 40
    n_floors = 20

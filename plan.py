""" A simple file to store the various building plans """
from strategy import BaseStrategy


class BasePlan(object):
    name = None    # The plan name
    n_els = 2      # The number of elevators
    n_iter = 30    # The number of iterations
    n_floors = 10  # The number of floors
    strategy = BaseStrategy


class Training1(BasePlan):
    name = "training_1"


class Training2(BasePlan):
    name = "training_2"
    n_els = 4
    n_iter = 40
    n_floors = 20


class Training3(Training2):
    name = "training_3"
    n_iter = 80


class Random1(BasePlan):
    name = "ch_rnd_500_1"
    n_iter = 500
    n_els = 4
    n_floors = 25


class Random2(Random1):
    name = "ch_rnd_500_2"


class Random3(Random1):
    name = "ch_rnd_500_3"


class Clustered1(Random1):
    name = "ch_clu_500_1"


class Clustered2(Clustered1):
    name = "ch_clu_500_2"


class Clustered3(Clustered1):
    name = "ch_clu_500_3"


class Realistic1(BasePlan):
    name = "ch_rea_1000_1"
    n_iter = 1000
    n_els = 8
    n_floors = 50


class Realistic2(Realistic1):
    name = "ch_rea_1000_2"


class Realistic3(Realistic1):
    name = "ch_rea_1000_3"

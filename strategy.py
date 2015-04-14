""" strategy.py - Include various strategies which could be included
in plan objects themselves, or added via CLI arguments
"""


class BaseStrategy(object):
    """ A base Strategy object """

    do_shuffle = True

    @classmethod
    def name(cls):
        return cls.__name__.lower()

    @classmethod
    def init_elevators(cls, elevators):
        """ Set some values for individual elevators, like initial
        conditions and home positions """

        pass

    @classmethod
    def distance_metric(cls, el, req):
        """ Customize a distance metric for making decisions """
        n_reqs = len(el.requests)
        n_btns = len(el.button_pressed)

        distance = abs(el.distance_to(req[0]))

        return distance * (n_reqs + n_btns) ** 2

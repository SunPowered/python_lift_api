""" elevator.py  - The elevator object """


class Elevator(object):
    """ An object to store current states of various elevators and assigned requests. """

    def __init__(self, id_):
        """ Main constructor. """

        self._id = id_
        self.requests = []
        self.button_pressed = []
        self.speed = 0
        self.direction = 0

    def is_request_assigned(self, floor, direction):
        return (floor, direction) in self.requests

    def assign_request(self, floor, direction):
        """ Assign a request to the elevator """
        if not self.is_request_assigned(floor, direction):
            self.requests.append((floor, direction))

    def remove_request(self, floor, direction):
        """ Remove a request """
        if self.is_request_assigned(floor, direction):
            self.requests.remove((floor, direction))

    def requests_along_direction(self, direction):
        """ Get a sorted list of requests along a given direction """
        if direction != 1 and direction != -1:
            raise ValueError("Improper direction, please enter +/-1")

        def filter_direction(req):
            return req[1] == direction

        req = filter(filter_direction, self.requests)
        floors = list(zip(*req)[0])
        do_reverse = False
        if direction == -1:
            do_reverse = True
        floors.sort(reverse=do_reverse)
        return floors

    def is_button_pressed(self, btn):
        """ Simlpe check whether a button press is present """
        return btn in self.button_pressed

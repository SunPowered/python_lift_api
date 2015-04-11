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
        if self.is_request_assigned(floor, direction):
            self.requests.remove((floor, direction))


""" elevator.py  - The elevator object """
from boxlift_api import Command

class Elevator(object):
    """ An object to store current states of various elevators and assigned requests. """

    def __init__(self, id_):
        """ Main constructor. """

        self.id_ = id_
        self.requests = []
        self.button_pressed = []
        self.speed = 0
        self.direction = 0
        self.floor = 0

    def __str__(self):
        return "Elevator[{}] - {}: spd: {} dir.: {} btn: {} rqs: {}".format(self.id_, self.floor,
                                                                            self.speed, self.direction,
                                                                            self.button_pressed, self.requests)

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

    def has_requests(self):
        """ Simple check whether requests are assigned """
        return len(self.requests) > 0

    def closest_request(self):
        """ Return the direction to the closest request """
        if not self.requests:
            return None
        dist = [(req[0], self.distance_to(req[0])) for req in self.requests]
        dist.sort(key=lambda x: abs(x[1]))

        return self.direction_to(dist[0][0])

    def has_buttons(self):
        """ Simple check whether buttons are pressed """
        return len(self.button_pressed) > 0

    def has_any_requests(self):
        """ Does this have button presses or requests? """
        return self.has_requests() or self.has_buttons()

    def is_button_pressed(self, btn):
        """ Simlpe check whether a button press is present """
        return btn in self.button_pressed

    def distance_to(self, floor):
        """ Find the distance from the current position to the current floor """
        return floor - self.floor

    def direction_to(self, floor):
        """ Return the direction to a floor from current location """
        dist = self.distance_to(floor)
        return dist / abs(dist)

    def update_state(self, state):
        """ A quick method to update the current state of things based on the REST values """
        id_ = state.get('id', None)

        if id_ is None:
            raise TypeError("Undefined state structure, no id parameter")
        if id_ != self.id_:
            raise ValueError("Incorrect id parameter, try a different object")

        button_pressed = state.get('buttons_pressed', [])
        self.button_pressed = button_pressed

        floor = state.get('floor', 0)
        self.floor = floor

    def command(self, **kwargs):
        """ Format a command for this elevator """
        return Command(self.id_, **kwargs)

    def get_command(self):
        """ Determines what command to issue for itself """

        # If no requests and not at home, send home
        if self.floor != 0 and not self.has_any_requests():
            return self.command(speed=1, direction=-1)
        
        # If no requests, and at home, then do nothing
        if self.floor == 0 and not self.has_any_requests():
            return None

        # If current floor is pressed, then stop
        if self.speed and self.is_button_pressed(self.floor):
            return self.command(speed=0, direction=self.direction)

        # If current floor is requested, then stop and flip direction
        if self.speed and self.is_request_assigned(self.floor):
            return self.command(speed=0, direction=-1 * self.direction)

        # If stopped, then go towards next button
        if not self.speed and self.has_buttons():
            return self.command(speed=1, direction=self.direction_to(self.button_pressed[0]))

        # If stopped, and no buttons, go to nearest request
        if not self.speed and self.has_requests():
            direction = self.closest_request()
            return self.command(speed=1, direction=direction)
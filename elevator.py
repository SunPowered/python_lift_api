""" elevator.py  - The elevator object """
from boxlift_api import Command

NO_REQUEST_STAY_PUT = True


class Elevator(object):
    """ An object to store current states of various elevators and assigned requests. """

    def __init__(self, id_, n_floors):
        """ Main constructor. """

        self.id_ = id_
        self.requests = []
        self.button_pressed = []
        self.speed = 0
        self.direction = 0
        self.floor = 0
        self.n_floors = n_floors

    def __str__(self):
        return "Elevator[{}] - {}: spd: {} dir.: {} btn: {} rqs: {}".format(self.id_, self.floor,
                                                                            self.speed, self.direction,
                                                                            self.button_pressed, self.requests)

    def is_request_assigned(self, floor, direction=None):
        if len(self.requests) == 0:
            return False
        if direction is None:
            return floor in zip(*self.requests)[0]
        else:
            return (floor, direction) in self.requests

    def assign_request(self, floor, direction):
        """ Assign a request to the elevator """
        if not self.is_request_assigned(floor, direction):
            self.requests.append((floor, direction))

    def remove_request(self, floor, direction=None):
        """ Remove a request """
        if self.is_request_assigned(floor, direction=None):
            req = self.get_request_by_floor(floor)
            self.requests.remove(req)

    def get_request_by_floor(self, floor):
        for req in self.requests:
            if req[0] == floor:
                return req

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
        if dist == 0:
            return 0
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
        self.speed = kwargs.get('speed')
        self.direction = kwargs.get('direction')
        return Command(self.id_, **kwargs)

    def get_command(self):
        """ Determines what command to issue for itself """

        req = None
        if self.is_request_assigned(self.floor):
            req = self.get_request_by_floor(self.floor)

        # If no requests, then stay put
        if NO_REQUEST_STAY_PUT:
            if not self.has_any_requests():
                return None
        else:
            # If no requests and not at home, send home
            if self.floor != 0 and not self.has_any_requests():
                return self.command(speed=1, direction=-1)

            # If no requests, and at home, then do nothing
            if self.floor == 0 and not self.has_any_requests():
                return None

        # If current floor is requested, then stop and set proper direction
        if req is not None:
            if self.floor in [0, self.n_floors]:
                self.remove_request(self.floor)
                return self.command(speed=0, direction=req[1])
            elif (req[1] != self.direction) and self.has_buttons():
                return self.command(speed=0, direction=self.direction)
            else:
                self.remove_request(self.floor)
                return self.command(speed=0, direction=req[1])

        # If current floor is pressed, then stop
        if self.is_button_pressed(self.floor):
            if req is not None:
                return self.command(speed=0, direction=req[1])
            return self.command(speed=0, direction=self.direction)
        # if self.speed and self.is_button_pressed(self.floor):
        #     if self.is_request_assigned(self.floor):
        #         req = self.get_request_by_floor(self.floor)
        #         return self.command(speed=0, direction=req[1])
        #     return self.command(speed=0, direction=self.direction)

        # If stopped, then go towards next button
        if not self.speed and self.has_buttons() and req is None:
            return self.command(speed=1, direction=self.direction_to(self.button_pressed[0]))

        # If stopped, and no buttons, go to nearest request
        if not self.speed and self.has_requests():
            direction = self.closest_request()
            return self.command(speed=1, direction=direction)

        # All else considered, keep on keeping on
        return self.command(speed=self.speed, direction=self.direction)

""" elevator.py  - The elevator object """
from boxlift_api import Command

NO_REQUEST_STAY_PUT = True


class Elevator(object):
    """ An object to store current states of various elevators and assigned requests. """

    def __init__(self, id_, n_floors, debug=False):
        """ Main constructor. """

        self.id_ = id_
        self.requests = []
        self.button_pressed = []
        self.speed = 0
        self.direction = 1
        self.floor = 0
        self.n_floors = n_floors
        self.dp = debug
        self.home_floor = -1
        self.cmd_states = {1: 'Stopped: Send to Button Press',
                           2: 'Stopped: Send to Request',
                           3: 'Stopped: Send Home',
                           4: 'Stop at button: Move to closest request',
                           5: 'Stop at button: Turn around',
                           6: 'Stopping at Request',
                           7: 'Heading to Furthest Request',
                           8: 'Heading Home',
                           9: 'Keep on Keeping On'}

    def __str__(self):
        return "Elevator[{}] - {}: spd: {} dir.: {} btn: {} rqs: {}".format(self.id_, self.floor,
                                                                            self.speed, self.direction,
                                                                            self.button_pressed, self.requests)

    def print_cmd(self, cmd):
        if self.dp:
            print "CMD [{}] - {}: {}".format(self.id_, cmd, self.cmd_states[cmd])

    def print_info(self):
        print "[{}] - n_floors: {} - home_floor: {}".format(self.id_, self.n_floors, self.home_floor)

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

    def sort_requests_by_distance(self):
        if not self.requests:
            return None
        return sorted(self.requests, key=lambda x: self.distance_to(x[0]))

    def get_furthest_request(self):
        sorted_reqs = self.sort_requests_by_distance()
        if sorted_reqs is not None:
            return sorted_reqs[-1]

    def get_closest_request(self):
        sorted_reqs = self.sort_requests_by_distance()
        if sorted_reqs is not None:
            return sorted_reqs[0]

    def has_button_along_direction(self, direction):
        for btn in self.button_pressed:
            if self.direction_to(btn) == direction:
                return True
        return False

    def is_at_home(self):
        """ Is the elevator at it's home floor """
        return self.floor == self.home_floor or self.home_floor == -1

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

    def send_to_floor(self, floor):
        """ Send a command to go to a floor """
        return self.command(speed=1, direction=self.direction_to(floor))

    def stop_and_point(self, direction):
        """ Stop and orient towards a direction """
        return self.command(speed=0, direction=direction)

    def get_command(self):
        if not self.speed:
            # It's stopped!
            floor = None
            # If there is a button press, go that way
            if self.has_buttons():
                self.print_cmd(1)
                floor = self.button_pressed[0]
            # If requests are available, go to them
            elif self.has_requests():
                req = self.get_furthest_request()
                self.print_cmd(2)
                floor = req[0]
            elif not self.is_at_home():
                # Go home
                self.print_cmd(3)
                floor = self.home_floor
            if floor is not None:
                return self.send_to_floor(floor)

        else:
            # It's moving!

            has_button = self.is_button_pressed(self.floor)
            furthest_req = self.get_furthest_request()
            closest_request = self.get_closest_request()
            has_request = self.is_request_assigned(self.floor, self.direction)

            req = None
            direction = self.direction
            if self.floor == 0:
                direction = 1
            if self.floor == self.n_floors:
                direction = -1
            if has_request:
                req = self.get_request_by_floor(self.floor)

            do_stop = False
            if has_button:
                if self.has_button_along_direction(self.direction):
                    do_stop = True
                    direction = self.direction
                elif closest_request is not None:
                    # Head to closest request
                    self.print_cmd(4)
                    direction = self.direction_to(closest_request[0])
                    do_stop = True
                else:
                    direction = -1 * self.direction
                    self.print_cmd(5)
                    do_stop = True
            elif has_request:
                self.remove_request(*req)
                self.print_cmd(6)
                do_stop = True
            elif closest_request is not None:
                if closest_request[0] == self.floor:
                    self.remove_request(*closest_request)
                    self.print_cmd(6)
                    direction = closest_request[1]
                    do_stop = True
            elif furthest_req is not None:
                if furthest_req[0] == self.floor:
                    self.remove_request(*furthest_req)
                    self.print_cmd(6)
                    do_stop = True
                    direction = furthest_req[1]
                else:
                    self.print_cmd(7)
                    return self.command(speed=1, direction=self.direction_to(furthest_req[0]))
            elif not self.has_buttons() and not self.has_requests():
                #self.print_cmd(8)
                if self.is_at_home():
                    do_stop = True
                else:
                    direction = self.direction_to(self.home_floor)
            
            if do_stop:
                return self.stop_and_point(direction)
            else:
                self.print_cmd(9)
                return self.command(speed=1, direction=self.direction)

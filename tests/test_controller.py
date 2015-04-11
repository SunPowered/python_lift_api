import unittest

from controller import Controller
from elevator import Elevator
from plan import BasePlan


class TestPlan(BasePlan):
    name = "Test Plan"


class ControllerTest(unittest.TestCase):

    def setUp(self):
        self.controller = Controller(TestPlan)

    def configure_elevator(self, id_, floor=None, speed=None, direction=None, btns=None, reqs=None):
        el = self.controller.elevators[id_]
        if floor:
            el.floor = floor
        if speed:
            el.speed = speed
        if direction:
            el.direction = direction
        if btns:
            el.button_pressed = btns
        if reqs:
            el.requests = reqs

    def test_controller_init(self):

        class BadPlan(object):
            name = "I'm bad"

        self.assertRaises(TypeError, Controller, BadPlan)
        self.assertRaises(TypeError, Controller, BadPlan())

        self.assertEqual(len(self.controller.elevators), TestPlan.n_els)

        self.assertTrue(isinstance(self.controller.elevators[0], Elevator))

    def test_find_el_otw(self):
        req = (5, 1)

        # If all elevators are on the ground floor with no commands, None should be returned
        self.assertIsNone(self.controller.find_elevator_by_req_otw(req))

        # Setup the environment - easy
        self.configure_elevator(1, floor=2, speed=1, direction=1, btns=[3, 7])
        self.assertEqual(self.controller.find_elevator_by_req_otw(req), 1)

        self.controller.init_elevators()

        # Setup the environment - less easy
        self.configure_elevator(0, floor=6, speed=1, direction=-1, btns=[4, 1])
        self.assertEqual(self.controller.find_elevator_by_req_otw(req), 0)

        self.controller.init_elevators()
        self.configure_elevator(0, floor=2, speed=1, direction=-1, btns=[4, 3])

        self.assertIsNone(self.controller.find_elevator_by_req_otw(req))

        self.controller.init_elevators()
        self.configure_elevator(0, floor=2, speed=1, direction=1, btns=[4, 3])
        self.configure_elevator(1, floor=3, speed=1, direction=1, btns=[6, 5])
        self.assertEqual(self.controller.find_elevator_by_req_otw(req), 1)


if __name__ == '__main__':
    unittest.main()

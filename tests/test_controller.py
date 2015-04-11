import unittest

from controller import Controller
from elevator import Elevator
from plan import BasePlan


class TestPlan(BasePlan):
    name = "Test Plan"


class ControllerTest(unittest.TestCase):

    def setUp(self):
        self.controller = Controller(TestPlan)

    def test_controller_init(self):

        class BadPlan(object):
            name = "I'm bad"

        self.assertRaises(TypeError, Controller, BadPlan)
        self.assertRaises(TypeError, Controller, BadPlan())

        self.assertEqual(len(self.controller.elevators), TestPlan.n_els)

        self.assertTrue(isinstance(self.controller.elevators[0], Elevator))

if __name__ == '__main__':
    unittest.main()

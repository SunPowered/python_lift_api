""" Test the elevator object """

import unittest

from elevator import Elevator


class ElevatorTest(unittest.TestCase):

    def setUp(self):
        self.el = Elevator(0)

    def test_request_crud(self):
        self.assertFalse(self.el.is_request_assigned(1, -1))
        self.el.assign_request(1, -1)
        self.assertTrue(self.el.is_request_assigned(1, -1))
        self.el.remove_request(1, -1)
        self.assertFalse(self.el.is_request_assigned(1, -1))

    def test_button_pressed(self):
        self.assertFalse(self.el.is_button_pressed(2))
        self.el.button_pressed = [2, 5, 8]
        self.assertTrue(self.el.is_button_pressed(2))
        self.assertFalse(self.el.is_button_pressed(3))

    def test_requests_along_direction(self):
        self.assertRaises(ValueError, self.el.requests_along_direction, -2)

        for floor, direction in [(3, -1), (1, 1), (7, 1), (8, -1), (1, -1)]:
            self.el.assign_request(floor, direction)

        floors = self.el.requests_along_direction(-1)
        self.assertEqual(floors, [8, 3, 1])

        floors = self.el.requests_along_direction(1)
        self.assertEqual(floors, [1, 7])

if __name__ == '__main__':
    unittest.main()

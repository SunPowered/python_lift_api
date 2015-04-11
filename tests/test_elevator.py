""" Test the elevator object """

import unittest

from elevator import Elevator


class ElevatorTest(unittest.TestCase):

    def setUp(self):
        self.el = Elevator(0)

    def test_request_crud(self):
        self.assertFalse(self.el.is_request_assigned(1, -1))
        self.assertFalse(self.el.has_requests())
        self.el.assign_request(1, -1)
        self.assertTrue(self.el.is_request_assigned(1, -1))
        self.assertTrue(self.el.has_requests())
        self.el.remove_request(1, -1)
        self.assertFalse(self.el.is_request_assigned(1, -1))

    def test_button_pressed(self):
        self.assertFalse(self.el.is_button_pressed(2))
        self.assertFalse(self.el.has_buttons())
        self.el.button_pressed = [2, 5, 8]
        self.assertTrue(self.el.is_button_pressed(2))
        self.assertFalse(self.el.is_button_pressed(3))
        self.assertTrue(self.el.has_buttons())

    def test_requests_along_direction(self):
        self.assertRaises(ValueError, self.el.requests_along_direction, -2)

        for floor, direction in [(3, -1), (1, 1), (7, 1), (8, -1), (1, -1)]:
            self.el.assign_request(floor, direction)

        floors = self.el.requests_along_direction(-1)
        self.assertEqual(floors, [8, 3, 1])

        floors = self.el.requests_along_direction(1)
        self.assertEqual(floors, [1, 7])

    def test_distance_direction_to(self):
        self.el.floor = 2
        self.assertEqual(self.el.distance_to(3), 1)
        self.assertEqual(self.el.distance_to(0), -2)

        self.assertEqual(self.el.direction_to(5), 1)
        self.assertEqual(self.el.direction_to(0), -1)

    def test_update_state(self):
        bad_state = {'nid': 0}
        self.assertRaises(TypeError, self.el.update_state, bad_state)
        bad_state = {'id': 1}
        self.assertRaises(ValueError, self.el.update_state, bad_state)

        good_state = {'id': 0, 'floor': 1, 'buttons_pressed': [3, 5]}
        self.el.update_state(good_state)
        self.assertEqual(self.el.floor, 1)
        self.assertEqual(self.el.button_pressed, [3, 5])

if __name__ == '__main__':
    unittest.main()

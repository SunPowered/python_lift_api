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

if __name__ == '__main__':
    unittest.main()

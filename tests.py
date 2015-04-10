import unittest

import mock

from go import Go, TrainingPlan


class BaseTest(unittest.TestCase):

    def setUp(self):
        # Mock out the post request
        api_patcher = mock.patch('boxlift_api.BoxLift._post')
        self.api_patcher = api_patcher.start()
        self.api_patcher.return_value = {"id": "Test ID",
                                         "token": "Test token",
                                         "status": "in_progess",
                                         "building": "Test building",
                                         "visualization": "Test URL",
                                         "message": "Test Message",
                                         "elevators": [{"id": 0, "floor": 0, "buttons_pressed": []}, 
                                                       {"id": 1, "floor": 0, "buttons_pressed": []}],
                                         "requests": []}
        self.go = Go(TrainingPlan(), sandbox_mode=True)

    def test_api_mock(self):
        self.api_patcher.assert_called()
        self.assertTrue(self.go.state is not None)

    def test_request_assign(self):
        self.go.assign_request(0, 3)
        self.assertEqual(self.go.is_request_assigned(3), 0)
        self.go.assign_request(1, 6)
        self.assertTrue(self.go.is_request_assigned(6), 1)

        self.assertFalse(self.go.is_request_assigned(2))

        self.go.deassign_request(1, 6)
        self.assertFalse(self.go.is_request_assigned(6))

    def test_elevator_request(self):
        self.api_patcher.return_value['requests'] = [{"direction": -1, "floor": 3}]
        self.go.send_commands([])
        self.go.get_commands()
        self.assertTrue(self.go.is_request_assigned(3) is not False)
        self.assertFalse(3 in self.go.els[0]['accepted_requests'] and 3 in self.go.els[1]['accepted_requests'])

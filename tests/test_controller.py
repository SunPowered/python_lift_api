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

        # If all elevators are on the ground floor with no commands, one of them should be returned
        self.assertIsNotNone(self.controller.find_elevator_by_req_otw(req))

        # Setup the environment - easy
        self.configure_elevator(1, floor=2, speed=1, direction=1, btns=[3, 7])
        self.assertEqual(self.controller.find_elevator_by_req_otw(req), 1)

        self.controller.init_elevators()

        # Setup the environment - less easy
        self.configure_elevator(0, floor=6, speed=1, direction=-1, btns=[4, 1])
        self.assertEqual(self.controller.find_elevator_by_req_otw(req), 0)

        self.controller.init_elevators()
        self.configure_elevator(0, floor=2, speed=1, direction=-1, btns=[4, 3])

        self.assertEqual(self.controller.find_elevator_by_req_otw(req), 1)

        self.controller.init_elevators()
        self.configure_elevator(0, floor=2, speed=1, direction=1, btns=[4, 3])
        self.configure_elevator(1, floor=3, speed=1, direction=1, btns=[6, 5])
        self.assertEqual(self.controller.find_elevator_by_req_otw(req), 1)

    def test_find_el_metric(self):
        req = (5, 1)

        self.configure_elevator(0, floor=3)
        self.configure_elevator(1, floor=1)
        self.assertEqual(self.controller.find_elevator_by_req_metric(req), 0)

        self.controller.init_elevators()
        self.configure_elevator(0, floor=9)
        self.configure_elevator(1, floor=3, btns=[1, 2], reqs=[(3, -1), (0, 1)])
        self.assertEqual(self.controller.find_elevator_by_req_metric(req), 0)

    def test_assign_request(self):
        req = (5, 1)
        self.assertFalse(self.controller.is_request_assigned(req))
        self.controller.assign_request(req)
        self.assertTrue(self.controller.is_request_assigned(req))
        self.controller.assign_request(req)
        els = [el.id_ for el in self.controller.elevators if el.is_request_assigned(*req)]
        self.assertEqual(len(els), 1, els)

        req2 = (8, -1)
        self.controller.assign_request(req2)
        self.assertTrue(self.controller.is_request_assigned(req2))
        self.controller.assign_request(req2)

        els = [el.id_ for el in self.controller.elevators if el.is_request_assigned(*req2)]
        self.assertEqual(len(els), 1, els)
        
    def test_update(self):

        resp = {u'status': u'in_progress',
                u'elevators': [{u'id': 0, u'floor': 3},
                               {u'id': 1, u'floor': 2}],
                u'token': u'Test Token',
                u'floors': 10,
                u'requests': [],
                u'message': u'Building In Progress'}

        self.controller.update(resp)
        self.assertEqual(self.controller.elevators[0].floor, 3)

    def test_opposing_requests(self):
        self.configure_elevator(0, speed=1, direction=1, floor=5, reqs=[(3, -1)])
        self.assertEqual(self.controller.find_opposing_requests(), [((3, -1), 0)])

    def test_find_closest_el_not_moving_away(self):
        req = (3, -1)
        self.configure_elevator(0, speed=1, direction=1, floor=5, reqs=[req])
        self.configure_elevator(1, speed=1, direction=1, floor=2, reqs=[])
        self.assertEqual(self.controller.find_closest_el_not_moving_away(req), 1)

        self.configure_elevator(1, speed=1, direction=-1, floor=2, reqs=[])
        self.assertIsNone(self.controller.find_closest_el_not_moving_away(req))

    def test_shuffle_requests(self):
        req = (3, -1)
        self.configure_elevator(0, speed=1, direction=1, floor=5, reqs=[req])
        self.configure_elevator(1, speed=1, direction=1, floor=2)
        
        self.controller.shuffle_requests()

        self.assertTrue(self.controller.elevators[1].is_request_assigned(*req))
if __name__ == '__main__':
    unittest.main()

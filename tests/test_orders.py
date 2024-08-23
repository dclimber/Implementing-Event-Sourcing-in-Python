import unittest

import orders


class OrderAggregateTest(unittest.TestCase):

    def test_should_create_order(self):
        order = orders.Order.create(user_id=1)

        self.assertEqual(order.changes, [orders.OrderCreated(user_id=1)])

    def test_should_emit_set_status_event(self):
        order = orders.Order([orders.OrderCreated(user_id=1)])

        order.set_status("confirmed")

        self.assertEqual(order.changes, [orders.StatusChanged("confirmed")])

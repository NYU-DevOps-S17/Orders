# Test cases can be run with either of the following:
# python -m unittest discover
# nosetests -v --rednose --nologcapture

import unittest
import json
from redis import Redis
from werkzeug.exceptions import NotFound
from app.models import Order
from app.custom_exceptions import DataValidationError

######################################################################
#  T E S T   C A S E S
######################################################################
class TestOrders(unittest.TestCase):

    def setUp(self):
        Order.use_db(Redis(host='127.0.0.1', port=6379))
        Order.remove_all()

    def test_create_a_order(self):
        # Create a order and assert that it exists
        order = Order(0, "Tom", 200)
        self.assertNotEqual( order, None )
        self.assertEqual( order.id, 0 )
        self.assertEqual( order.customer_name, "Tom" )
        self.assertEqual( order.amount_paid, 200 )

    def test_add_a_order(self):
        # Create a order and add it to the database
        orders = Order.all()
        self.assertEqual( orders, [])
        order = Order(0, "Tom", 200)
        self.assertTrue( order != None )
        self.assertEqual( order.id, 0 )
        order.save()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual( order.id, 1 )
        orders = Order.all()
        self.assertEqual( len(orders), 1)
        self.assertEqual( orders[0].id, 1 )
        self.assertEqual( orders[0].customer_name, "Tom" )
        self.assertEqual( orders[0].amount_paid, 200 )

    def test_update_a_order(self):
        order = Order(0, "Tom", 200)
        order.save()
        self.assertEqual( order.id, 1 )
        # Change it an save it
        order.amount_paid = 700
        order.save()
        self.assertEqual( order.id, 1 )
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        orders = Order.all()
        self.assertEqual( len(orders), 1)
        self.assertEqual( orders[0].amount_paid, 700)
        self.assertEqual( orders[0].customer_name, "Tom" )

    def test_delete_a_order(self):
        order = Order(0, "Tom", 200)
        order.save()
        self.assertEqual( len(Order.all()), 1)
        # delete the order and make sure it isn't in the database
        order.delete()
        self.assertEqual( len(Order.all()), 0)

    def test_serialize_a_order(self):
        order = Order(0, "Tom", 200)
        data = order.serialize()
        self.assertNotEqual( data, None )
        self.assertIn( 'id', data )
        self.assertEqual( data['id'], 0 )
        self.assertIn( 'customer_name', data )
        self.assertEqual( data['customer_name'], "Tom" )
        self.assertIn( 'amount_paid', data )
        self.assertEqual( data['amount_paid'], 200 )

    def test_deserialize_a_order(self):
        data = {"id":1, "customer_name": "Bob", "amount_paid": 300}
        order = Order(data['id'])
        order.deserialize(data)
        self.assertNotEqual( order, None )
        self.assertEqual( order.id, 1 )
        self.assertEqual( order.customer_name, "Bob" )
        self.assertEqual( order.amount_paid, 300 )

    def test_deserialize_a_order_with_no_name(self):
        data = {"id":0, "amount_paid": 300}
        order = Order(0)
        self.assertRaises(DataValidationError, order.deserialize, data)

    def test_deserialize_a_order_with_no_data(self):
        order = Order(0)
        self.assertRaises(DataValidationError, order.deserialize, None)

    def test_deserialize_a_order_with_bad_data(self):
        order = Order(0)
        self.assertRaises(DataValidationError, order.deserialize, "string data")

    def test_find_order(self):
        Order(0, "Tom", 200).save()
        Order(0, "Bob", 300).save()
        order = Order.find(2)
        self.assertIsNot( order, None)
        self.assertEqual( order.id, 2 )
        self.assertEqual( order.customer_name, "Bob" )

    def test_find_with_no_orders(self):
        order = Order.find(1)
        self.assertIs( order, None)

    def test_find_or_404(self):
        self.assertRaises(NotFound, Order.find_or_404, 1)

    def test_order_not_found(self):
        Order(0, "Tom", 200).save()
        order = Order.find(2)
        self.assertIs( order, None)

    def test_find_by_amount_paid(self):
        Order(0, "Tom", 200).save()
        Order(0, "Bob", 300).save()
        orders = Order.find_by_amount_paid(300)
        self.assertNotEqual( len(orders), 0 )
        self.assertEqual( orders[0].amount_paid, 300 )
        self.assertEqual( orders[0].customer_name, "Bob" )


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestOrders)
    # unittest.TextTestRunner(verbosity=2).run(suite)

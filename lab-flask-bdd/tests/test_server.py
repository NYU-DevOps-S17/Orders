# Test cases can be run with either of the following:
# python -m unittest discover
# nosetests -v --rednose --nologcapture

import unittest
import logging
import json
from app import server

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409

######################################################################
#  T E S T   C A S E S
######################################################################
class TestOrderServer(unittest.TestCase):

    def setUp(self):
        server.app.debug = True
        server.app.logger.addHandler(logging.StreamHandler())
        server.app.logger.setLevel(logging.CRITICAL)

        self.app = server.app.test_client()
        server.inititalize_redis()
        server.data_reset()
        server.data_load({"customer_name": "Tom", "amount_paid": "200"})
        server.data_load({"customer_name": "Bob", "amount_paid": "300"})

    def test_index(self):
        resp = self.app.get('/')
        self.assertEqual( resp.status_code, HTTP_200_OK )
        self.assertTrue ('Order Demo REST API Service' in resp.data)

    def test_get_order_list(self):
        resp = self.app.get('/orders')
        self.assertEqual( resp.status_code, HTTP_200_OK )
        self.assertTrue( len(resp.data) > 0 )

    def test_get_order(self):
        resp = self.app.get('/orders/2')
        #print 'resp_data: ' + resp.data
        self.assertEqual( resp.status_code, HTTP_200_OK )
        data = json.loads(resp.data)
        self.assertEqual (data['customer_name'], 'Bob')

    def test_get_order_not_found(self):
        resp = self.app.get('/orders/0')
        self.assertEqual( resp.status_code, HTTP_404_NOT_FOUND )

    def test_create_order(self):
        # save the current number of orders for later comparrison
        order_count = self.get_order_count()
        # add a new order
        new_order = {'customer_name': 'Kate', 'amount_paid': '400'}
        data = json.dumps(new_order)
        resp = self.app.post('/orders', data=data, content_type='application/json')
        self.assertEqual( resp.status_code, HTTP_201_CREATED )
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertTrue( location != None)
        # Check the data is correct
        new_json = json.loads(resp.data)
        self.assertEqual (new_json['customer_name'], 'Kate')
        # check that count has gone up and includes Kate
        resp = self.app.get('/orders')
        # print 'resp_data(2): ' + resp.data
        data = json.loads(resp.data)
        self.assertEqual( resp.status_code, HTTP_200_OK )
        self.assertEqual( len(data), order_count + 1 )
        self.assertIn( new_json, data )

    def test_update_order(self):
        new_order = {'customer_name': 'Bob', 'amount_paid': '500'}
        data = json.dumps(new_order)
        resp = self.app.put('/orders/2', data=data, content_type='application/json')
        self.assertEqual( resp.status_code, HTTP_200_OK )
        resp = self.app.get('/orders/2', content_type='application/json')
        self.assertEqual( resp.status_code, HTTP_200_OK )
        new_json = json.loads(resp.data)
        self.assertEqual (new_json['amount_paid'], '500')

    def test_update_order_with_no_customer_name(self):
        new_order = {'amount_paid': '200'}
        data = json.dumps(new_order)
        resp = self.app.put('/orders/2', data=data, content_type='application/json')
        self.assertEqual( resp.status_code, HTTP_400_BAD_REQUEST )

    def test_update_order_not_found(self):
        new_order = {"customer_name": "ossso", "amount_paid": '3000'}
        data = json.dumps(new_order)
        resp = self.app.put('/orders/0', data=data, content_type='application/json')
        self.assertEquals( resp.status_code, HTTP_404_NOT_FOUND )

    def test_delete_order(self):
        # save the current number of orders for later comparrison
        order_count = self.get_order_count()
        # delete a order
        resp = self.app.delete('/orders/2', content_type='application/json')
        self.assertEqual( resp.status_code, HTTP_204_NO_CONTENT )
        self.assertEqual( len(resp.data), 0 )
        new_count = self.get_order_count()
        self.assertEqual( new_count, order_count - 1)

    def test_create_order_with_no_customer_name(self):
        new_order = {'amount_paid': '200'}
        data = json.dumps(new_order)
        resp = self.app.post('/orders', data=data, content_type='application/json')
        self.assertEqual( resp.status_code, HTTP_400_BAD_REQUEST )

    def test_create_order_with_no_content_type(self):
        new_order = {'amount_paid': '200'}
        data = json.dumps(new_order)
        resp = self.app.post('/orders', data=data)
        self.assertEqual( resp.status_code, HTTP_400_BAD_REQUEST )

    def test_get_nonexisting_order(self):
        resp = self.app.get('/orders/5')
        self.assertEqual( resp.status_code, HTTP_404_NOT_FOUND )

    def test_query_order_list(self):
        resp = self.app.get('/orders', query_string='amount_paid=200')
        self.assertEqual( resp.status_code, HTTP_200_OK )
        self.assertTrue( len(resp.data) > 0 )
        self.assertTrue( 'Tom' in resp.data)
        self.assertFalse( 'Bob' in resp.data)
        data = json.loads(resp.data)
        query_item = data[0]
        self.assertEqual(query_item['amount_paid'], '200')
        
    def test_duplicate_nonexisting_order(self):
        resp = self.app.put('/orders/11/duplicate')
        self.assertEqual(resp.status_code, HTTP_404_NOT_FOUND)
        
    def test_duplicate_existing_order(self):
        order_count_old = self.get_order_count()
        resp = self.app.put('/orders/1/duplicate')
        self.assertEqual(resp.status_code,HTTP_201_CREATED)
        order_count_new = self.get_order_count()
        self.assertEqual(order_count_new,order_count_old+1)

######################################################################
# Utility functions
######################################################################

    def get_order_count(self):
        # save the current number of orders
        resp = self.app.get('/orders')
        self.assertEqual( resp.status_code, HTTP_200_OK )
        data = json.loads(resp.data)
        return len(data)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()

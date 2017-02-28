# Copyright 2016, 2017 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from threading import Lock
from flask import Flask, Response, jsonify, request, json
from orders import *

# Create Flask application
app = Flask(__name__)

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409

# Lock for thread-safe counter increment
lock = Lock()

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    orders_url = request.base_url + "orders"
    return jsonify(name='Orders Demo REST API Service',
                   version='1.0',
                   url=orders_url
                   ), HTTP_200_OK

######################################################################
# LIST ALL Orders
######################################################################
@app.route('/orders', methods=['GET'])
def list_orders():
	results = orders.values()
	amount_paid = request.args.get('amount_paid')
	customer_name = request.args.get('customer_name')
	if amount_paid:
		results = []
		for key, value in orders.iteritems():
			if str(value['amount_paid']) == str(amount_paid):
				results.append(orders[key])
	elif customer_name:
		results = []
		for key, value in orders.iteritems():
			if str(value['customer_name']).lower() == str(customer_name).lower():
				results.append(orders[key])
				
	return reply(results, HTTP_200_OK)

######################################################################
# RETRIEVE A Order
######################################################################
@app.route('/orders/<int:id>', methods=['GET'])
def get_orders(id):
    if orders.has_key(id):
        message = orders[id]
        rc = HTTP_200_OK
    else:
        message = { 'error' : 'Order with id: %s was not found' % str(id) }
        rc = HTTP_404_NOT_FOUND

    return reply(message, rc)

######################################################################
# ADD A NEW Order
######################################################################
@app.route('/orders', methods=['POST'])
def create_orders():
    payload = request.get_json()
    if is_valid(payload):
        id = next_index()
        orders[id] = {'id': id, 'customer_name': payload['customer_name'], 'amount_paid': payload['amount_paid']}
        message = orders[id]
        rc = HTTP_201_CREATED
    else:
        message = { 'error' : 'Data is not valid' }
        rc = HTTP_400_BAD_REQUEST

    return reply(message, rc)

######################################################################
# UPDATE AN EXISTING Order
######################################################################
@app.route('/orders/<int:id>', methods=['PUT'])
def update_orders(id):
    if orders.has_key(id):
        payload = request.get_json()
        if is_valid(payload):
            orders[id] = {'id': id, 'customer_name': payload['customer_name'], 'amount_paid': payload['amount_paid']}
            message = orders[id]
            rc = HTTP_200_OK
        else:
            message = { 'error' : 'Order data was not valid' }
            rc = HTTP_400_BAD_REQUEST
    else:
        message = { 'error' : 'Order %s was not found' % id }
        rc = HTTP_404_NOT_FOUND

    return reply(message, rc)

######################################################################
# DELETE A Order
######################################################################
@app.route('/orders/<int:id>', methods=['DELETE'])
def delete_orders(id):
    del orders[id];
    return '', HTTP_204_NO_CONTENT

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def next_index():
    global current_order_id
    with lock:
        current_order_id += 1
    return current_order_id

def reply(message, rc):
    response = Response(json.dumps(message))
    response.headers['Content-Type'] = 'application/json'
    response.status_code = rc
    return response

def is_valid(data):
    valid = False
    try:
        customer_name = data['customer_name']
        amount_paid = data['amount_paid']
        valid = True
    except KeyError as err:
        app.logger.error('Missing parameter error: %s', err)
    return valid


######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    current_order_id = 2
    # Pull options from environment
    debug = (os.getenv('DEBUG', 'False') == 'True')
    port = os.getenv('PORT', '5000')
    app.run(host='0.0.0.0', port=int(port), debug=debug)

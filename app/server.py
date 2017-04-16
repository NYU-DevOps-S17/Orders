######################################################################
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
######################################################################

import os
import logging
from redis import Redis
from redis.exceptions import ConnectionError
from flask import Flask, Response, jsonify, request, json, url_for, make_response
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import NotFound
from models import Order
from . import app

# Error handlers reuire app to be initialized so we must import
# then only after we have initialized the Flask app instance
import error_handlers

redis = None

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    # data = '{customer_name: <string>, amount_paid: <string>}'
    # url = request.base_url + 'orders' # url_for('list_orders')
    # return jsonify(customer_name='Order Demo REST API Service', version='1.0', url=url, data=data), status.HTTP_200_OK
    return app.send_static_file('index.html')

######################################################################
# LIST ALL ORDERS
######################################################################
@app.route('/orders', methods=['GET'])
def list_orders():
    """
    Retrieve a list of Orders
    This endpoint will return all Orders unless a query parameter is specificed
    ---
    tags:
      - Orders
    description: The Orders endpoint allows you to query Orders
    parameters:
      - name: customer_name
        in: query
        description: the name of the customer who placed the Order
        required: false
        type: string
    responses:
      200:
        description: An array of Orders
        schema:
          type: array
          items:
            schema:
              id: Order
              properties:
                id:
                  type: integer
                  description: unique id assigned internally by service
                customer_name:
                  type: string
                  description: the name of the person who placed the order
                amount_paid:
                  type: integer
                  description: the amount the order came out to
    """
    orders = []
    customer_name = request.args.get('customer_name')
    if customer_name:
        orders = Order.find_by_customer_name(customer_name)
    else:
        orders = Order.all()

    results = [order.serialize() for order in orders]
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# RETRIEVE A ORDER
######################################################################
@app.route('/orders/<int:id>', methods=['GET'])
def get_orders(id):
    """
    Retrieve a single Order
    This endpoint will return a Order based on it's id
    ---
    tags:
      - Orders
    produces:
      - application/json
    parameters:
      - name: id
        in: path
        description: ID of order to retrieve
        type: integer
        required: true
    responses:
      200:
        description: Order returned
        schema:
          id: Order
          properties:
            id:
              type: integer
              description: unique id assigned internallt by service
            customer_name:
              type: string
              description: the name of the person who placed the order
            amount_paid:
              type: integer
              description: the amount the order came out to
      404:
        description: Order not found
    """
    order = Order.find_or_404(id)
    return make_response(jsonify(order.serialize()), status.HTTP_200_OK)

######################################################################
# ADD A NEW ORDER
######################################################################
@app.route('/orders', methods=['POST'])
def create_orders():
    """
    Creates a Order
    This endpoint will create a Order based the data in the body that is posted
    ---
    tags:
      - Orders
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: data
          required:
            - name
            - category
          properties:
            customer_name:
              type: string
              description: the name of the person who placed the order
            amount_paid:
              type: integer
              description: the amount the order came out to
    responses:
      201:
        description: Order created
        schema:
          id: Order
          properties:
            id:
              type: integer
              description: unique id assigned internally by service
            customer_name:
              type: string
              description: the name of the person who placed the order
            amount_paid:
              type: integer
              description: the amount the order came out to
      400:
        description: Bad Request (the posted data was not valid)
    """
    # Check for form submission data
    print 'Headers: {}'.format(request.headers.get('Content-Type'))
    data = {}
    if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
        data = {'customer_name': request.form['customer_name'], 'amount_paid': request.form['amount_paid']}
    else:
        data = request.get_json()
    order = Order()
    order.deserialize(data)
    order.save()
    message = order.serialize()
    return make_response(jsonify(message), status.HTTP_201_CREATED, {'Location': order.self_url() })

######################################################################
# UPDATE AN EXISTING ORDER
######################################################################
@app.route('/orders/<int:id>', methods=['PUT'])
def update_orders(id):
    """
    Update a Order
    This endpoint will update a Order based the body that is posted
    ---
    tags:
      - Orders
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: id
        in: path
        description: ID of order to retrieve
        type: integer
        required: true
      - in: body
        name: body
        schema:
          id: data
          required:
            - name
            - category
          properties:
            customer_name:
              type: string
              description: the name of the person who placed the order
            amount_paid:
              type: integer
              description: the amount the order came out to
    responses:
      200:
        description: Order Updated
        schema:
          id: Order
          properties:
            id:
              type: integer
              description: unique id assigned internallt by service
            customer_name:
              type: string
              description: the name of the person who placed the order
            amount_paid:
              type: integer
              description: the amount the order came out to
      400:
        description: Bad Request (the posted data was not valid)
    """
    order = Order.find_or_404(id)
    order.deserialize(request.get_json())
    order.save()
    return make_response(jsonify(order.serialize()), status.HTTP_200_OK)

######################################################################
# DELETE A ORDER
######################################################################
@app.route('/orders/<int:id>', methods=['DELETE'])
def delete_orders(id):
    # """
    # Delete a Order
    # This endpoint will delete a Order based the id specified in the path
    # ---
    # tags:
    #   - Orders
    # description: Deletes a Order from the database
    # parameters:
    #   - name: id
    #     in: path
    #     description: ID of order to delete
    #     type: integer
    #     required: true
    # responses:
    #   204:
    #     description: Order deleted
    # """
    order = Order.find(id)
    if order:
        order.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
# DUPLICATE A Order
######################################################################
@app.route('/orders/<int:id>/duplicate', methods=['PUT'])
def duplicate_order(id):
    """
    Duplicates a Order
    This endpoint will create a Order with the same customer name and amount paid based a previous order that was posted
    ---
    tags:
      - Orders
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: id
        in: path
        description: ID of order to retrieve
        type: integer
        required: true
    responses:
      201:
        description: Order created
        schema:
          id: Order
          properties:
            id:
              type: integer
              description: unique id assigned internally by service
            customer_name:
              type: string
              description: the name of the person who placed the order
            amount_paid:
              type: integer
              description: the amount the order came out to
      404:
        description: Order not found
    """
    order = Order.find(id)
    if order:
        message = order.serialize()
        data = {}
        data = {'customer_name': message['customer_name'], 'amount_paid': message['amount_paid']}
        order = Order()
    	order.deserialize(data)
    	order.save()
        message = order.serialize()
        return make_response(jsonify(message), status.HTTP_201_CREATED, {'Location': order.self_url() })
    else:
        message = { 'error' : 'Order with id: %s was not found' % str(id) }
        return make_response(jsonify(message), status.HTTP_400_BAD_REQUEST)


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
# load sample data
def data_load(data):
    Order().deserialize(data).save()

# empty the database
def data_reset():
    redis.flushall()

@app.before_first_request
def setup_logging():
    if not app.debug:
        # In production mode, add log handler to sys.stderr.
        handler = logging.StreamHandler()
        handler.setLevel(app.config['LOGGING_LEVEL'])
        # formatter = logging.Formatter(app.config['LOGGING_FORMAT'])
        #'%Y-%m-%d %H:%M:%S'
        formatter = logging.Formatter('[%(asctime)s] - %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)

######################################################################
# Connect to Redis and catch connection exceptions
######################################################################
def connect_to_redis(hostname, port, password):
    redis = Redis(host=hostname, port=port, password=password)
    try:
        redis.ping()
    except ConnectionError:
        redis = None
    return redis


######################################################################
# INITIALIZE Redis
# This method will work in the following conditions:
#   1) In Bluemix with Redis bound through VCAP_SERVICES
#   2) With Redis running on the local server as with Travis CI
#   3) With Redis --link ed in a Docker container called 'redis'
######################################################################
def inititalize_redis():
    global redis
    redis = None
    # Get the crdentials from the Bluemix environment
    if 'VCAP_SERVICES' in os.environ:
        app.logger.info("Using VCAP_SERVICES...")
        VCAP_SERVICES = os.environ['VCAP_SERVICES']
        services = json.loads(VCAP_SERVICES)
        creds = services['rediscloud'][0]['credentials']
        app.logger.info("Conecting to Redis on host %s port %s" % (creds['hostname'], creds['port']))
        redis = connect_to_redis(creds['hostname'], creds['port'], creds['password'])
    else:
        app.logger.info("VCAP_SERVICES not found, checking localhost for Redis")
        redis = connect_to_redis('127.0.0.1', 6379, None)
        if not redis:
            app.logger.info("No Redis on localhost, using: redis")
            redis = connect_to_redis('redis', 6379, None)
    if not redis:
        # if you end up here, redis instance is down.
        app.logger.error('*** FATAL ERROR: Could not connect to the Redis Service')
    # Have the Order model use Redis
    Order.use_db(redis)

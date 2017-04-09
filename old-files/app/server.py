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
import logging
from redis import Redis
from redis.exceptions import ConnectionError
from flask import Flask, Response, jsonify, request, json, url_for, make_response
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import NotFound
from models import Orders
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
    return app.send_static_file('index.html')


######################################################################
# LIST ALL Orders
######################################################################
@app.route('/orders', methods=['GET'])
def list_orders():
    orders = []
    amount_paid = request.args.get('amount_paid')
    if amount_paid:
        orders = Order.find_by_amount_paid(amount_paid)
    else:
        orders = Order.all()

    results = [order.serialize() for order in orders]
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# RETRIEVE A Order
######################################################################
@app.route('/orders/<int:id>', methods=['GET'])
def get_orders(id):
    order = Order.find_or_404(id)
    return make_response(jsonify(order.serialize()), status.HTTP_200_OK)


######################################################################
# ADD A NEW Order
######################################################################
@app.route('/orders', methods=['POST'])
def create_orders():
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
# UPDATE AN EXISTING Order
######################################################################
@app.route('/orders/<int:id>', methods=['PUT'])
def update_orders(id):
    order = Order.find_or_404(id)
    order.deserialize(request.get_json())
    order.save()
    return make_response(jsonify(order.serialize()), status.HTTP_200_OK)


######################################################################
# DELETE A Order
######################################################################
@app.route('/orders/<int:id>', methods=['DELETE'])
def delete_orders(id):
    order = Order.find(id)
    if order:
        order.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
# DUPLICATE A Order
######################################################################
@app.route('/orders/<int:id>/duplicate', methods=['PUT'])
def duplicate_order(id):
    if orders.has_key(id):
        message = orders[id]

        new_id = next_index()
        orders[new_id] = {'id': new_id, 'customer_name': message['customer_name'], 'amount_paid': message['amount_paid']}
        message = orders[new_id]
        rc = HTTP_201_CREATED
    else:
        message = { 'error' : 'Order with id: %s was not found' % str(id) }
        rc = HTTP_404_NOT_FOUND

    return reply(message, rc)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
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

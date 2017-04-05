######################################################################
# Copyright 2016, 2017 John Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

from flask import url_for
from werkzeug.exceptions import NotFound
from custom_exceptions import DataValidationError

######################################################################
# Order Model for database
#   This class must be initialized with use_db(redis) before using
#   where redis is a value connection to a Redis database
######################################################################
class Order(object):
    __redis = None

    def __init__(self, id=0, customer_name=None, amount_paid=None):
        self.id = int(id)
        self.customer_name = customer_name
        self.amount_paid = amount_paid

    def self_url(self):
        return url_for('get_orders', id=self.id, _external=True)

    def save(self):
        if self.customer_name == None:
            raise AttributeError('customer_name attribute is not set')
        if self.id == 0:
            self.id = self.__next_index()
        Order.__redis.hmset(self.id, self.serialize())

    def delete(self):
        Order.__redis.delete(self.id)

    def __next_index(self):
        return Order.__redis.incr('index')

    def serialize(self):
        return { "id": self.id, "customer_name": self.customer_name, "amount_paid": self.amount_paid }

    def deserialize(self, data):
        try:
            self.customer_name = data['customer_name']
            self.amount_paid = data['amount_paid']
        except KeyError as e:
            raise DataValidationError('Invalid order: missing ' + e.args[0])
        except TypeError as e:
            raise DataValidationError('Invalid order: body of request contained bad or no data')
        return self

######################################################################
#  S T A T I C   D A T A B S E   M E T H O D S
######################################################################

    @staticmethod
    def use_db(redis):
        Order.__redis = redis

    @staticmethod
    def remove_all():
        Order.__redis.flushall()

    @staticmethod
    def all():
        # results = [Order.from_dict(redis.hgetall(key)) for key in redis.keys() if key != 'index']
        results = []
        for key in Order.__redis.keys():
            if key != 'index':  # filer out our id index
                data = Order.__redis.hgetall(key)
                order = Order(data['id']).deserialize(data)
                results.append(order)
        return results

    @staticmethod
    def find(id):
        if Order.__redis.exists(id):
            data = Order.__redis.hgetall(id)
            order = Order(data['id']).deserialize(data)
            return order
        else:
            return None

    @staticmethod
    def find_or_404(id):
        order = Order.find(id)
        if not order:
            raise NotFound("Order with id '{}' was not found.".format(id))
        return order

    @staticmethod
    def find_by_customer_name(customer_name):
        # return [order for order in Order.__data if order.amount_paid == amount_paid]
        results = []
        for key in Order.__redis.keys():
            if key != 'index':  # filer out our id index
                data = Order.__redis.hgetall(key)
                if data['customer_name'] == customer_name:
                    results.append(Order(data['id']).deserialize(data))
        return results

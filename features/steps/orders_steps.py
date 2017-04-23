from behave import *
import json
from app import server

@when(u'I visit the "home page"')
def step_impl(context):
    context.resp = context.app.get('/')

@then(u'I should see "{message}"')
def step_impl(context, message):
    assert message in context.resp.data

@then(u'I should not see "{message}"')
def step_impl(context, message):
    assert message not in context.resp.data

@given(u'the following orders')
def step_impl(context):
    server.data_reset()
    for row in context.table:
        server.data_load({"customer_name": row['customer_name'], "amount_paid": row['amount_paid']})

@when(u'I visit "{url}"')
def step_impl(context, url):
    context.resp = context.app.get(url)
    assert context.resp.status_code == 200

@when(u'I attempt to query for "{url}" and search by customer name "{customer_name}"')
def step_impl(context, url, customer_name):
    context.resp = context.app.get(url + '?customer_name=' + customer_name)
    assert context.resp.status_code == 200

@when(u'I delete "{url}" with id "{id}"')
def step_impl(context, url, id):
    target_url = url + '/' + id
    context.resp = context.app.delete(target_url)
    assert context.resp.status_code == 204
    assert context.resp.data is ""

@when(u'I retrieve "{url}" with id "{id}"')
def step_impl(context, url, id):
    target_url = url + '/' + id
    context.resp = context.app.get(target_url)
    assert context.resp.status_code == 200

@when(u'I change "{key}" to "{value}"')
def step_impl(context, key, value):
    data = json.loads(context.resp.data)
    data[key] = value
    context.resp.data = json.dumps(data)

@when(u'I update "{url}" with id "{id}"')
def step_impl(context, url, id):
    target_url = url + '/' + id
    context.resp = context.app.put(target_url, data=context.resp.data, content_type='application/json')
    assert context.resp.status_code == 200

@when(u'I use "{url}" the id "{id}" of that order so the customer can re-order their previous order')
def step_impl(context, url, id):
    target_url = url + '/' + id + '/duplicate'
    context.resp = context.app.put(target_url, data=context.resp.data, content_type='application/json')
    assert context.resp.status_code == 201

@then(u'I should see an order on "{url}" with the same amount_paid and customer name as the original order')
def step_impl(context, url):
    context.resp = context.app.get(url, data=context.resp.data, content_type='application/json')
    data = json.loads(context.resp.data)
    found = False

    for entry in data:
        for compare_entry in data:
            if entry['id'] == compare_entry['id']:
                continue
            if entry['customer_name'] == compare_entry['customer_name'] and entry['amount_paid'] == compare_entry['amount_paid']:
                found = True

    assert found == True

# @then(u'I should see a list of orders')
# def step_impl(context):
#     assert context.resp.status_code == 200
#     assert len(context.resp.data) > 0

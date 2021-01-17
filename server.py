from flask import Flask
from flask import request
import os.path
import pandas as pd
import time
import random
import json
from flask import jsonify
import ast
import numpy as np
import uuid

app = Flask(__name__)

########## globals

patients_file = 'patients.txt'
orders_file = 'orders.csv'
stock_file = 'stock.txt'
food_boxes_file = 'food_boxes.txt'

known_items = ['cucumbers','tomatoes','onions','carrots','beef','pork','chicken','bacon','oranges','apples','avocado','mango','cabbage','cheese']

########## API info

@app.route('/')
def hello_world():
    return '\
register_patient?patient_id=...\n\
order_box?urgency=...\n\
order_status?order_id=...\n'

########### helper functions below

def register_new_patient(patient_id):
    with open(patients_file, "a+") as f:
        f.write(patient_id+"\n")

def already_registered(patient_id):
    if os.path.isfile(patients_file):
        with open(patients_file) as f:
            all_patients = f.readlines()
            all_patients = [item.split('\n')[0] for item in all_patients]
            if str(patient_id) in all_patients:
                return True
    return False

def get_order_status(order_id):
    if os.path.isfile(orders_file):
        with open(orders_file) as f:
            all_orders = f.readlines()
            for item in all_orders:
                if item[0] == order_id:
                    return item[0]
    return -1

def get_stock_prices():
    if os.path.isfile(stock_file):
        with open(stock_file) as f:
            all_prices = f.readlines()

    return all_prices[1:]

def lookup_item_price(prices, item_id):
    for item_price in prices:
        if int(item_id) == int(item_price.split(',')[0]):
            return item_price.split(',')[2]

def place_order_(items_ordered):
    if os.path.isfile(orders_file):
        num_lines = sum(1 for line in open(orders_file))
        new_order_id = num_lines+1
        new_record = str(new_order_id)
        with open(orders_file, 'a') as f:

            for i in range(1, len(known_items)):
                new_record += ","+str(sum([item[1] if int(item[0]) == i else 0 for item in items_ordered])) if i in [item[0] for item in items_ordered] else ",0"
            new_record += ",0" #not delivered
            new_record += "\n"

            f.write(new_record)

    return new_order_id

############ endpoints below

@app.route('/register_patient')
def register_patient():
    if 'patient_id' in request.args:
        patient_id = request.args.get('patient_id')

        if already_registered(patient_id):
            return ('already registered\n')
        else:
            register_new_patient(patient_id)
            return ('registered new\n')

    return 'must specify patient_id'

@app.route('/order_box')
def order_box():
    if 'urgency' in request.args:
        urgency = request.args.get('urgency')

        if urgency == '1':
            return ('need to be delivered urgently')
        else:
            return ('not urgent delivery')


@app.route('/order_status')
def order_status():
    if 'order_id' in request.args:
        order_id = request.args.get('order_id')

        order_status = get_order_status(order_id)

        return order_status

@app.route('/get_food_boxes')
def get_food_boxes():
    with open(food_boxes_file) as f:
        json_data = json.load(f)
        return jsonify(json_data)

@app.route('/get_prices')
def get_prices():
    with open(stock_file) as f:
        all_prices = f.readlines()[1:]
        all_prices = [[item.split(',')[0], item.split(',')[1], item.split(',')[2]] for item in all_prices]
        print (all_prices)
        return str(np.array(all_prices).flatten())

@app.route('/place_order', methods=['POST'])
def place_order():
    total_price = 0

    if request.json != None:

        items_ordered = []

        prices = get_stock_prices()

        a_box = json.loads(str(request.json).replace("'", "\""))

        for order_item in a_box['contents']:
            items_ordered.append((order_item['id'], order_item['quantity']))
            order_item_price = lookup_item_price(prices, order_item['id'])
            total_price += float(order_item_price) * int(order_item['quantity'])

        new_order_id = place_order_(items_ordered)

    return str(new_order_id)# + "_" + str(total_price)

@app.route('/request_order_status')
def request_order_status():
    if 'order_id' in request.args:
        order_status = -2

        with open(orders_file) as f:
            all_orders = f.readlines()[1:]

            order_status = sum([int(item.split('\n')[0].split(',')[-1]) if int(item.split('\n')[0].split(',')[0])==int(request.args['order_id']) else 0 for item in all_orders])

    return str(order_status)

@app.route('/cancel_order')
def cancel_order():
    if 'order_id' in request.args:

        found = False

        with open(orders_file, 'r+') as f:
            all_orders = f.readlines()[1:]

            for idx, an_order in enumerate(all_orders):
                if int(an_order.split(',')[0]) == int(request.args['order_id']):
                    found = True
                    all_orders[idx] = ','.join(an_order.split('\n')[0].split(',')[:-1]) + ',-1\n'

            f.truncate(0)

        with open(orders_file, 'r+') as f:
            f.write('%s' % 'order_id,'+','.join(known_items)+',status\n')
            for updated_row in all_orders:
                f.write("%s" % updated_row)

    return 1 if found else -1


if __name__ == '__main__':
    app.run(host= '0.0.0.0', threaded=False, processes=10)

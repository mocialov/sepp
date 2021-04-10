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
import string
import names
from threading import Lock
from time import gmtime, strftime

app = Flask(__name__)

########## globals

individuals_file = 'shielding_individuals.txt'
orders_file = 'orders.csv'
sup_orders_file = 'supermarket_orders.csv'
stock_file = 'stock.txt'
food_boxes_file = 'food_boxes.txt'
providers_file = 'providers.txt'
providers_file2 = 'supermarkets.txt'

known_items = ['cucumbers','tomatoes','onions','carrots','beef','pork','chicken','bacon','oranges','apples','avocado','mango','cabbage','cheese']

#for atomic updates
lock = Lock()

########## API info

@app.route('/')
def hello_world():
    return ''

####### helper classes

class PHS(object):
    @staticmethod
    def verifyShieldingIndividual(CHI):
        return ['EH'+str(random.randint(1,17))+' '+str(random.randint(1,9))+random.choice(string.ascii_letters).upper()+random.choice(string.ascii_letters).upper(),
                ''.join([random.choice(string.ascii_letters) for _ in range(0, random.randint(5,9))]).lower(),
                ''.join([random.choice(string.ascii_letters) for _ in range(0, random.randint(5,9))]).lower(),
                ''.join([str(random.randint(0,10)) for _ in range(0, 11)])]


class DeliveryStatus:
    PLACED = 0
    PACKED = 1
    DISPATCHED = 2
    DELIVERED = 3
    CANCELLED = 4

########

########### helper functions below

def already_registered_provider(provider_id, postcode):
    with lock:
        if os.path.isfile(providers_file):
            with open(providers_file) as f:
                all_providers = f.readlines()
                all_providers = [item.split('\n')[0] for item in all_providers]
                for a_provider in all_providers:
                    if len(a_provider.split(',')) > 1:
                        if str(provider_id) in a_provider.split(',')[1] and str(postcode) in a_provider.split(',')[2]:
                            return True
    return False

def register_new_provider(provider_id, postcode):
    with lock:
        num_lines = sum(1 for line in open(providers_file))
        with open(providers_file, 'a+') as f:
            f.write(str(num_lines)+","+provider_id+","+postcode+"\n")
            return num_lines


def already_registered_provider_(provider_id, postcode):
    with lock:
        if os.path.isfile(providers_file):
            with open(providers_file2) as f:
                all_providers = f.readlines()
                all_providers = [item.split('\n')[0] for item in all_providers]
                for a_provider in all_providers:
                    if len(a_provider.split(',')) > 1:
                        if str(provider_id) in a_provider.split(',')[1] and str(postcode) in a_provider.split(',')[2]:
                            return True
    return False

def register_new_provider_(provider_id, postcode):
    with lock:
        num_lines = sum(1 for line in open(providers_file2))
        with open(providers_file2, 'a+') as f:
            f.write(str(num_lines)+","+provider_id+","+postcode+"\n")
            return num_lines

def register_new_individual(individual_id, postcode, name, surname, phone_number):
    with lock:
        with open(individuals_file, "a+") as f:
            f.write(individual_id+","+postcode+","+name+","+surname+","+phone_number+"\n")

def already_registered(individual_id):
    with lock:
        if os.path.isfile(individuals_file):
            with open(individuals_file) as f:
                all_individuals = f.readlines()
                all_individuals = [item.split(',')[0] for item in all_individuals]
                if str(individual_id) in all_individuals:
                    return True
    return False

def get_order_status(order_id):
    with lock:
        if os.path.isfile(orders_file):
            with open(orders_file) as f:
                all_orders = f.readlines()
                for item in all_orders:
                    if str(item.split(',')[0]) == str(order_id):
                        return item.split(',')[-1]
    return -1

def get_stock_prices():
    with lock:
        if os.path.isfile(stock_file):
            with open(stock_file) as f:
                all_prices = f.readlines()

    return all_prices[1:]

def lookup_item_price(prices, item_id):
    for item_price in prices:
        if int(item_id) == int(item_price.split(',')[0]):
            return item_price.split(',')[2]

def place_order_(items_ordered, individual_id, catering_id):
    with lock:
        if os.path.isfile(orders_file):
            num_lines = sum(1 for line in open(orders_file))
            new_order_id = num_lines+1
            new_record = str(new_order_id)
            with open(orders_file, 'a') as f:

                for i in range(1, len(known_items)+1):
                    new_record += ","+str(sum([item[1] if int(item[0]) == i else 0 for item in items_ordered])) if i in [item[0] for item in items_ordered] else ",0"
                new_record += ","+individual_id
                new_record += ","+catering_id
                new_record += ","+strftime("%Y-%m-%dT%H:%M:%S", gmtime()) #ordered time
                new_record += "," #packed time
                new_record += "," #dispatched time
                new_record += "," #delivered time
                new_record += ","+str(DeliveryStatus.PLACED)
                new_record += "\n"

                f.write(new_record)

    return new_order_id


def update_order_(items_ordered, order_id):
    found = False
    trying_to_increase_quantity = False
    with lock:
        if os.path.isfile(orders_file):
            new_records = []
            with open(orders_file) as f:
                for an_order in f.readlines():
                    print (an_order.split(',')[0], order_id)
                    if an_order.split(',')[0] == order_id and an_order.split(',')[-1].rstrip('\n') == str(DeliveryStatus.PLACED):
                        print ('found')
                        found = True
                        new_record = str(order_id)
                        for i in range(1, len(known_items)+1):
                            if int(an_order.split(',')[i]) < int(sum([item[1] if int(item[0]) == i else 0 for item in items_ordered])):
                                trying_to_increase_quantity = True

                            new_record += ","+str(sum([item[1] if int(item[0]) == i else 0 for item in items_ordered])) if i in [item[0] for item in items_ordered] else ",0"
                        new_record += ","+an_order.split(",")[len(an_order.split(','))-7]
                        new_record += ","+an_order.split(",")[len(an_order.split(','))-6]
                        new_record += ","+an_order.split(",")[len(an_order.split(','))-5]
                        new_record += ","+an_order.split(",")[len(an_order.split(','))-4]
                        new_record += ",,"
                        new_record += ","+str(DeliveryStatus.PLACED)
                        new_record += "\n"

                        if not trying_to_increase_quantity:
                            new_records.append(new_record)
                        else:
                            new_records.append(an_order)
                    else:
                        new_records.append(an_order)

            print (new_records)
            with open(orders_file, 'w') as f:
                for new_record in new_records:
                    f.write(new_record)
    return found if not trying_to_increase_quantity else not found


def update_order_status(order_id, new_status, dst):
    changed = False
    with lock:
        if os.path.isfile(orders_file if dst == 'caterer' else sup_orders_file):
            new_records = []
            with open(orders_file if dst == 'caterer' else sup_orders_file) as f:
                for an_order in f.readlines():
                    print (an_order.split(',')[0], order_id)
                    if an_order.split(',')[0] == order_id:

                        an_order = an_order.split(',')

                        current_status = int(an_order[-1])

                        if new_status == DeliveryStatus.CANCELLED:
                            if current_status != DeliveryStatus.DISPATCHED and \
                                current_status != DeliveryStatus.DELIVERED and \
                                current_status != DeliveryStatus.CANCELLED:
                                an_order[-1] = str(new_status)+'\n'
                                changed = True
                        else:
                            if new_status > current_status:
                                an_order[-1] = str(new_status)+'\n'
                                changed = True

                                if new_status == DeliveryStatus.PACKED:
                                    an_order[-4] = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
                                elif new_status == DeliveryStatus.DISPATCHED:
                                    an_order[-3] = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
                                elif new_status == DeliveryStatus.DELIVERED:
                                    an_order[-2] = strftime("%Y-%m-%dT%H:%M:%S", gmtime())

                        new_records.append(','.join(an_order))
                    else:
                        new_records.append(an_order)

            print (new_records)
            with open(orders_file if dst=='caterer' else sup_orders_file, 'w') as f:
                for new_record in new_records:
                    f.write(new_record)

    return changed



def individual_is_registered(individual_id):
    with lock:
        with open(individuals_file) as f:
            for a_individual in f.readlines():
                a_individual = a_individual.rstrip('\n').split(',')[0]
                print (individual_id, a_individual, individual_id==a_individual)
                if str(individual_id) == str(a_individual):
                    return True

    return False

def catering_is_registered(business_name, business_postcode):
    print ("finding catering", business_name, business_postcode)
    with lock:
        with open(providers_file) as f:
            for a_catering in f.readlines():
                a_catering = a_catering.rstrip('\n').split(',')
                if len(a_catering) > 1:
                    if str(a_catering[1]) == str(business_name) and str(a_catering[2]) == str(business_postcode):
                        #print (catering_id, a_catering, catering_id==a_catering)
                        #if str(catering_id) == str(a_catering):
                        return True
    return False

def get_catering_id(business_name, business_postcode):
    with lock:
        with open(providers_file) as f:
            for a_catering in f.readlines():
                a_catering = a_catering.rstrip('\n').split(',')
                if len(a_catering) > 1:
                    if str(a_catering[1]) == str(business_name) and str(a_catering[2]) == str(business_postcode):
                        return a_catering[0]
    return -1

def get_supermarket_id(business_name, business_postcode):
    with lock:
        with open(providers_file2) as f:
            for a_supermarket in f.readlines():
                a_supermarket = a_supermarket.rstrip('\n').split(',')
                if len(a_supermarket) > 1:
                    if str(a_supermarket[1]) == str(business_name) and str(a_supermarket[2]) == str(business_postcode):
                        return a_supermarket[0]
    return -1

############ endpoints below

@app.route('/registerCateringCompany')
def register_provider():
    if 'business_name' in request.args and 'postcode' in request.args:
        provider_id = request.args.get('business_name')
        postcode = request.args.get('postcode')

        if already_registered_provider(provider_id, postcode):
            return ('already registered')
        else:
            new_id = register_new_provider(provider_id, postcode)
            return ('registered new') #return (str(new_id))

    return 'must specify provider_id'


@app.route('/registerSupermarket')
def registerSupermarket():
    if 'business_name' in request.args and 'postcode' in request.args:
        provider_id = request.args.get('business_name')
        postcode = request.args.get('postcode')

        if already_registered_provider_(provider_id, postcode):
            return ('already registered')
        else:
            new_id = register_new_provider_(provider_id, postcode)
            return ('registered new') #return (str(new_id))

    return 'must specify provider_id'


@app.route('/registerShieldingIndividual')
def register_individual():
    if 'CHI' in request.args:
        individual_id = request.args.get('CHI')

        postcode, name, surname, phone_number = PHS.verifyShieldingIndividual(individual_id)

        if already_registered(individual_id):
            return ('already registered')
        else:
            register_new_individual(individual_id, postcode, name, surname, phone_number)
            return jsonify([postcode, name, surname, phone_number])
            #return ('registered new\n')

    return 'must specify CHI'

@app.route('/order_box')
def order_box():
    if 'urgency' in request.args:
        urgency = request.args.get('urgency')

        if urgency == '1':
            return ('need to be delivered urgently')
        else:
            return ('not urgent delivery')


@app.route('/requestStatus')
def order_status():
    if 'order_id' in request.args:
        order_id = request.args.get('order_id')

        order_status = get_order_status(order_id)

        return str(order_status)

@app.route('/cancelOrder')
def cancelOrder():
    if 'order_id' in request.args:
        order_id = request.args.get('order_id')

        new_status = 0

        found = update_order_status(order_id, DeliveryStatus.CANCELLED, 'caterer')

        return str(found)

    return 'must provide order_id'


@app.route('/showFoodBox')
def get_food_boxes():
    if True:#if 'orderOption' in request.args and 'dietaryPreference' in request.args:
        order_option = request.args.get('orderOption', default='', type=str)
        dietary_preference = request.args.get('dietaryPreference', default='', type=str)

        with lock:
            with open(food_boxes_file) as f:
                json_data = json.load(f)

                if dietary_preference == '':
                    json_data = [x for x in json_data]
                else:
                    json_data = [x for x in json_data if x['diet'] == dietary_preference]

                return jsonify(json_data)

    return 'something is wrong'

@app.route('/get_prices')
def get_prices():
    with lock:
        with open(stock_file) as f:
            all_prices = f.readlines()[1:]
            all_prices = [[item.split(',')[0], item.split(',')[1], item.split(',')[2]] for item in all_prices]
            print (all_prices)
            return str(np.array(all_prices).flatten())


@app.route('/placeOrder', methods=['POST'])
def placeOrder():
    total_price = 0
    individual_max = False
    if 'individual_id' in request.args and 'catering_business_name' in request.args and 'catering_postcode' in request.args and individual_is_registered(request.args.get('individual_id')) and catering_is_registered(request.args.get('catering_business_name'), request.args.get('catering_postcode')):
        if request.json != None:
            #dateTime = " ".join(request.args['dateTime'].split("_"))
            individual_id = request.args['individual_id']
            catering_id = get_catering_id(request.args.get('catering_business_name'), request.args.get('catering_postcode'))

            items_ordered = []

            prices = get_stock_prices()

            a_box = json.loads(str(request.json).replace("'", "\""))

            total_quantity = 0
            for order_item in a_box['contents']:
                items_ordered.append((order_item['id'], order_item['quantity']))
                order_item_price = lookup_item_price(prices, order_item['id'])
                total_price += float(order_item_price) * int(order_item['quantity'])
                total_quantity += int(order_item['quantity'])
                #if int(order_item['quantity']) >= 3:
                #    individual_max = True

            if True:#total_quantity <= 10 and not individual_max:
                new_order_id = place_order_(items_ordered, individual_id, catering_id)
            else:
                new_order_id = -1

        return str(new_order_id)# + "_" + str(total_price)
    else:
        return 'must provide individual_id and catering_id. The individual and the catering must be registered before placing an order'


@app.route('/editOrder', methods=['POST'])
def editOrder():
    if 'order_id' in request.args:

        if request.json != None:
            #dateTime = " ".join(request.args['dateTime'].split("_"))

            items_ordered = []

            a_box = json.loads(str(request.json).replace("'", "\""))

            for order_item in a_box['contents']:
                items_ordered.append((order_item['id'], order_item['quantity']))

            updated = update_order_(items_ordered, request.args['order_id'])

            return str(updated)
    else:
        return 'must provide order_id'



@app.route('/request_order_status')
def request_order_status():
    if 'order_id' in request.args:
        order_status = -2

        with lock:
            with open(orders_file) as f:
                all_orders = f.readlines()[1:]

                order_status = sum([int(item.split('\n')[0].split(',')[-1]) if int(item.split('\n')[0].split(',')[0])==int(request.args['order_id']) else 0 for item in all_orders])

    return str(order_status)


@app.route('/updateOrderStatus')
def update_order_status_():
    if 'order_id' in request.args and 'newStatus' in request.args:
        order_id = request.args.get('order_id')
        new_status = None
        if request.args['newStatus'].lower() == 'delivered':
            new_status = DeliveryStatus.DELIVERED
        elif request.args['newStatus'].lower() == 'packed':
            new_status = DeliveryStatus.PACKED
        elif request.args['newStatus'].lower() == 'dispatched':
            new_status = DeliveryStatus.DISPATCHED

        if new_status != None:
            found = update_order_status(order_id, new_status, 'caterer')
            return str(found)
        else:
            return 'can either deliver, pack, or dispatch the order'

    return 'must provide order_id and newStatus'

@app.route('/distance')
def distance():
    if 'postcode1' in request.args and 'postcode2' in request.args:
        postcode1 = request.args.get('postcode1')
        postcode2 = request.args.get('postcode2')

        edinburgh_diameter = 18334 #m
        max_cost = 99*10 + 25*2 + 9

        postcode1 = postcode1.replace('EH', '', 1) #assuming edinburgh
        postcode2 = postcode2.replace('EH', '', 1) #assuming edinburgh

        postcode1 = postcode1.split('_')
        postcode1_first_part = postcode1[0]
        postcode1_second_part = postcode1[1]

        postcode2 = postcode2.split('_')
        postcode2_first_part = postcode2[0]
        postcode2_second_part = postcode2[1]

        first_part_postcode_differences = abs(int(postcode1_first_part) - int(postcode2_first_part))

        total_cost = 1 * (first_part_postcode_differences * 10)

        for idx, _ in enumerate(postcode1_second_part):

            letter_cost = 0

            if postcode1_second_part[idx].lower() in string.ascii_lowercase and postcode2_second_part[idx].lower() in string.ascii_lowercase:
                letter1 = string.ascii_lowercase.index(postcode1_second_part[idx].lower())
                letter2 = string.ascii_lowercase.index(postcode2_second_part[idx].lower())
                letter_cost = abs(letter1 - letter2)
            elif postcode1_second_part[idx].lower().isdigit() and postcode2_second_part[idx].lower().isdigit():
                letter_cost = abs(int(postcode1_second_part[idx].lower()) - int(postcode2_second_part[idx].lower()))

            total_cost += letter_cost

        return str(edinburgh_diameter * total_cost / max_cost)

@app.route('/getCaterers')
def get_caterers():
    with lock:
        with open(providers_file) as f:
            content = f.readlines()
            content = [item.rstrip('\n') for item in content]
    return jsonify(content)

@app.route('/getCateringCompanyforOrder')
def get_catering_company_for_order():
    if 'order_id' in request.args:
        with lock:
            with open(orders_file) as f:
                content = f.readlines()
                content = [item.rstrip('\n') for item in content]

                for idx, item in enumerate(content):
                    if str(item.split(',')[0]) == str(request.args.get('order_id')):
                        with open(providers_file) as f2:
                            content2 = f2.readlines()
                            content2 = [item_.rstrip('\n') for item_ in content2]

                            for item2 in content2:
                                if str(item2.split(',')[0]) == str(item.split(',')[16]):
                                    return jsonify([item2.split(',')[1], item2.split(',')[2]])
        return str(-1)

    return 'must specify order_id'

def order_exists(order_number):
    with open(sup_orders_file) as f:
        for a_line in f.readlines():
            if len(a_line.split(',')) > 0:
                if str(a_line.split(',')[0]) == str(order_number):
                    return True
    return False


@app.route('/recordSupermarketOrder')
def record_supermarket_order():
    if 'individual_id' in request.args and 'order_number' in request.args and 'supermarket_business_name' in request.args and 'supermarket_postcode' in request.args and individual_is_registered(request.args.get('individual_id')) and get_supermarket_id(request.args.get('supermarket_business_name'), request.args.get('supermarket_postcode')) != -1:

        order_number = request.args['order_number']
        individual_id = request.args['individual_id']
        supermarket_id = get_supermarket_id(request.args.get('supermarket_business_name'), request.args.get('supermarket_postcode'))

        if order_exists(order_number): return 'False'

        with lock:
            #num_lines = sum(1 for line in open(sup_orders_file))
            #new_order_id = num_lines+1
            new_record = str(order_number) #str(new_order_id)

            with open(sup_orders_file, 'a+') as f:
                new_record += ","+individual_id
                new_record += ","+supermarket_id
                new_record += ","+strftime("%Y-%m-%dT%H:%M:%S", gmtime()) #ordered time
                new_record += "," #packed time
                new_record += "," #dispatched time
                new_record += "," #delivered time
                new_record += ","+str(DeliveryStatus.PLACED)
                new_record += "\n"
                f.write(new_record)

            return 'True' #str(new_order_id)

    return 'require individual_id, order_number, supermarket_business_name, and supermarket_postcode. The individual must be registered and the supermarket must be registered'


@app.route('/updateSupermarketOrderStatus')
def update_supermarket_order_status():
    if 'order_id' in request.args and 'newStatus' in request.args:
        order_id = request.args.get('order_id')
        new_status = None

        if request.args['newStatus'].lower() == 'delivered':
            new_status = DeliveryStatus.DELIVERED
        elif request.args['newStatus'].lower() == 'packed':
            new_status = DeliveryStatus.PACKED
        elif request.args['newStatus'].lower() == 'dispatched':
            new_status = DeliveryStatus.DISPATCHED

        if new_status != None:
            found = update_order_status(order_id, new_status, 'supermarket')
            return str(found)
        else:
            return 'can either deliver, pack, or dispatch the order'

    return 'must provide order_id and newStatus'

if __name__ == '__main__':
    app.run(host= '0.0.0.0', threaded=False, processes=10)

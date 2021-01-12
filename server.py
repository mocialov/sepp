from flask import Flask
from flask import request
import os.path
import pandas as pd

app = Flask(__name__)

########## globals

patients_file = 'patients.txt'
orders_file = 'orders.csv'

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

from flask import (
    Blueprint, render_template, request, url_for, make_response
)
from flask_cors import CORS

import json
# logging
from logzero import logger
# common tools
from flaskapp.api.common import get_trans_id, get_bool
from envparse import Env

import xmlrpc.client
from datetime import datetime

env = Env(
    TerminalID=str,
    TermialPass=str,
    MonthLoadMax=int,
    MaxBalance=int,
    MinLoad=int
)
env.read_envfile()

# get db connection
from flaskapp.mongoconnection import db_init
paydnadb = db_init()

# token authentication handling
from flaskapp.auth import jwt_required

# tutuka tools TODO: probably be replace by transaction library
from flaskapp.api.tutuka import tutuka_xmlrpc
xml_client = tutuka_xmlrpc.Tutuka_XMLRPC({'terminalID' : env('TerminalID'), 'terminalPassword' : env('TerminalPass')})

from flaskapp.api import transactions

bp = Blueprint('cards', __name__, url_prefix='/api/cards')
CORS(bp)

def to_xml_date(datetimeformat):
    return xmlrpc.client.DateTime(datetimeformat)

def get_month_load_todate(card):
    month_balance = 0
    today = datetime.now()
    start_date = datetime(today.year, today.month, 1)
    profile_id = paydnadb.cards.find_one({'_id': card}).get('profile_id')
    resp = xml_client.statement_by_date_range(profile_id, card, to_xml_date(start_date), to_xml_date(today), get_trans_id())

    for statement_line in resp.get('statement'):
        if statement_line.get('transactionType') == 1:
            month_balance += statement_line.get('transactionAmount')
    return month_balance

@bp.route('/', methods=['GET'])
@jwt_required('super')
def get_cards():
    cards = []
    for card in paydnadb.cards.find({}, {'authNum': 0}):
        cards.append(card)
    return make_response({ "cards": cards }, 200)

@bp.route('/<string:id>', methods=['GET'])
@jwt_required('super')
def get_card(id):
    return make_response({ "card": paydnadb.cards.find_one({'_id': id}, {'authNum': 0}) }, 200)

@bp.route('/<string:id>/transactions', methods=['GET'])
def get_cardtrans(id):
    return make_response({ "card": paydnadb.transaction_q.find_one({'card': id})}, 200)

@bp.route('/load/<string:id>', methods=['POST'])
@jwt_required('super')
def load_card(id):
    print(request.form.items())
    if request.method == 'POST':
        load_value = int(request.form.get('loadValue'))
        qued_by = request.form.get('username')
        # add to load transq
        resp = transactions.load_to_que(id, 'load', load_value, 'user-from-jwt')
        if resp.get('resultCode') == 1 and resp != None:
            return { "action": f'card loaded with R{(load_value / 100.0):.2f}' }
        else:
            return { "loadError": resp.get('resultText')}
    else:
        return make_response({'Error': 'method not allowed'}, 401)

@bp.route('/insertfee/<string:id>', methods=['POST'])
def insert_card_fee():
    return make_response({'result': 'Card fee added'})

@bp.route('/deduct/<string:id>', methods=['POST'])
def deduct_card(id):
    print(request.args)
    if request.method == 'POST':
        card_dets = paydnadb.cards.find_one({'_id': id})
        current_bal = card_dets.get('balance') if card_dets.get('balance') else 0
        deduct_value = int(request.args.get('deductValue'))
        print(current_bal - deduct_value)
        if ((current_bal - deduct_value) >= 0):
            resp = xml_client.deduct_card_load_profile(card_dets.get('profile_id'), card_dets.get('_id'), deduct_value, get_trans_id())
            print(resp)
            if resp.get('resultCode') == 1:
                paydnadb.cards.update_one({'_id': id}, {'$set': {'balance': current_bal - deduct_value}})
                return { "action": f'card deducted with R{(deduct_value / 100.0):.2f}' }
            else:
                return { "deductError": resp.get('resultText')}
        else:
            return { "deductError": 'Insufficient funds on card', 'cardBalance': current_bal }
    else:
        return make_response({'Error': 'method not allowed'}, 401)

@bp.route('/monthly-load-balance/<string:id>', methods=['GET'])
def month_load_balance(id):
    monthly_load = get_month_load_todate(id)
    paydnadb.cards.find_one_and_update({'_id': id}, {'$set': {'monthlyLoadBalance': monthly_load}})
    return make_response({ "loadToDate": monthly_load, 'currentBalance': paydnadb.cards.find_one({'_id': id}).get('balance') }, 200)

@bp.route('/status/<string:id>', methods=['GET'])
def card_status(id):
    skipped_fields =['clientTransactionID', 'serverTransactionID', 'resultCode', 'resultText']
    card_dets = paydnadb.cards.find_one({'_id': id})
    resp = xml_client.status(card_dets.get('profile_id'), card_dets.get('_id'), get_trans_id())
    status = {}
    for k, v in resp.items():
        if k not in skipped_fields:
            status[k] = get_bool(v)
    if status != {}:
        paydnadb.cards.update_one({'_id': id}, {'$set': {'status': status}})
        return make_response({ "status": status}, 200)
    else:
        return make_response({'error': 'Error getting status for the card'})

@bp.route('/balance/<string:id>', methods=['GET'])
@jwt_required('super')
def card_balance(id):
    card_dets = paydnadb.cards.find_one({'_id': id})
    resp = xml_client.balance(card_dets.get('profile_id'), card_dets.get('_id'), get_trans_id())
    if resp.get('resultCode') == 1:
        paydnadb.cards.update_one({'_id': id}, {'$set': {'balance': resp['balanceAmount']}})
        return make_response({ "balance": resp['balanceAmount']}, 200)
    else:
        return make_response({'error': 'Error getting status for the card'})

@bp.route('/transq/<string:id>', methods=['GET'])
@jwt_required('super')
def transaction_q(id):
    card_dets = paydnadb.transaction_q.find({'card': id})
    if resp.get('resultCode') == 1:
        paydnadb.cards.update_one({'_id': id}, {'$set': {'balance': resp['balanceAmount']}})
        return make_response({ "balance": resp['balanceAmount']}, 200)
    else:
        return make_response({'error': 'Error getting status for the card'})
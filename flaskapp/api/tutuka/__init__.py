from flask import (
    Blueprint, render_template, request, url_for
)
from flask_cors import CORS

import json
# logging
from logzero import logger
from flaskapp.api.common import get_trans_id
from envparse import Env

env = Env(
    TerminalID=str,
    TermialPass=str
)
env.read_envfile()

# get db connection
from flaskapp.mongoconnection import db_init
paydnadb = db_init()

from flaskapp.api.tutuka import tutuka_xmlrpc
xml_client = tutuka_xmlrpc.Tutuka_XMLRPC({'terminalID' : env('TerminalID'), 'terminalPassword' : env('TerminalPass')})

bp = Blueprint('tutuka', __name__, url_prefix='/api/tutuka')
CORS(bp)

def pid_to_name(pid):
    return paydnadb.profiles.find_one({'_id': pid}, {'name': 1}).get('name')

def name_to_pid(name):
    return paydnadb.profiles.find_one({'name': name}, {'_id': 1}).get('_id')

@bp.route('/balance', methods=['GET'])
def get_balance():
    profilename = request.args.get('profilename')
    profile = { k:v for (k,v) in [profile.items() for profile in PROFILES if profile['name'] == profilename][0] }
    card = request.args.get('card')
    pID = profile.get('profileID')
    logger.info(f'Card balance for {profilename} ({pID}), {card}')
    resp = xml_client.balance(pID, card, get_trans_id())
    if resp.get('resultCode') == 1:
        logger.info(f"Balance response: card: {resp.get('cardNumber')}, 'expiryDate': {resp.get('expiryDate').value}, 'balance': {resp.get('balanceAmount')}, 'transactionID': {resp.get('clientTransactionID')}")
        return { 'card': resp.get('cardNumber'), 'expiryDate': resp.get('expiryDate').value, 'balance': resp.get('balanceAmount'), 'transactionID': resp.get('clientTransactionID') }
    else:
        return resp

@bp.route('/profilebalance/<string:profilename>', methods=['GET'])
def get_profilebalance(profilename):
    print(profilename)
    profileID = name_to_pid(profilename)
    print(profileID)
    if profileID != '':
        resp = xml_client.profile_balance(profileID, get_trans_id())
    # return { 'profile': resp.get('cardNumber'), 'expiryDate': resp.get('expiryDate').value, 'balance': resp.get('balanceAmount'), 'transactionID': resp.get('clientTransactionID') }
    if resp.get('resultCode') == 1:
        paydnadb.profiles.update_one({'name': profilename}, {'$set': {'balance': resp.get('balanceAmount')}})
        return { 'profile': profilename, 'balance': resp.get('balanceAmount') }
    else:
        return { 'result': resp.get('resultText')}

@bp.route('/profiles', methods=['GET'])
def get_profiles():
    profiles = []
    for profile in paydnadb.profiles.find({}):
        profiles.append(profile)
    return { "profiles": profiles }

@bp.route('/profiles/<string:name>', methods=['GET'])
def get_profile(name):
    return { "profile": paydnadb.profiles.find_one({'name': name}, {'_id': 0}) }

@bp.route('/profiles/<string:name>/cards', methods=['GET'])
def get_profile_cards(name):
    profile_cards = [x for x in paydnadb.cards.find({'profile_id': name_to_pid(name)})]
    return { "cards": profile_cards }

@bp.route('/cards', methods=['GET'])
def get_cards():
    cards = []
    for card in paydnadb.cards.find({}, {'authNum': 0}):
        cards.append(card)
    return { "cards": cards }

@bp.route('/cards/<id>', methods=['GET'])
def get_card(id):
    return { "card": paydnadb.cards.find_one({'_id': id}, {'authNum': 0}) }

@bp.route('/', methods=['GET'])
def root():
    return '<<< Tutuka API >>>'
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

from flaskapp.api.tutuka import tutuka_xmlrpc
xml_client = tutuka_xmlrpc.Tutuka_XMLRPC({'terminalID' : env('TerminalID'), 'terminalPassword' : env('TerminalPass')})

tutukabp = Blueprint('tutuka', __name__, url_prefix='/api/tutuka')
CORS(tutukabp)

PROFILES = [{ "name": "sandbox", "profileID": "4731098549"}, { "name": "dummy", "profileID": "1235497356" }]

@tutukabp.route('/balance', methods=['GET'])
def get_balance():
    profilename = request.args.get('profilename')
    profile = { k:v for (k,v) in [profile.items() for profile in PROFILES if profile['name'] == profilename][0] }
    card = request.args.get('card')
    logger.info(f'Card balance for {profilename}, {card}')
    resp = xml_client.balance(profile.get('name'), card, get_trans_id())
    if resp.get('resultCode') == 1:
        logger.info(f"Balance response: card: {resp.get('cardNumber')}, 'expiryDate': {resp.get('expiryDate').value}, 'balance': {resp.get('balanceAmount')}, 'transactionID': {resp.get('clientTransactionID')}")
        return { 'card': resp.get('cardNumber'), 'expiryDate': resp.get('expiryDate').value, 'balance': resp.get('balanceAmount'), 'transactionID': resp.get('clientTransactionID') }
    else:
        return resp

@tutukabp.route('/profilebalance', methods=['GET'])
def get_profilebalance():
    profilename = request.args.get('profilename')
    profile = { k:v for (k,v) in [profile.items() for profile in PROFILES if profile['name'] == profilename][0] }
    print(profile)
    if profile != {}:
        resp = xml_client.profile_balance(profile['name'], get_trans_id())
    # return { 'profile': resp.get('cardNumber'), 'expiryDate': resp.get('expiryDate').value, 'balance': resp.get('balanceAmount'), 'transactionID': resp.get('clientTransactionID') }
    return { 'resp': resp }

@tutukabp.route('/profiles', methods=['GET'])
def get_profiles():
    return { "profiles": PROFILES }

@tutukabp.route('/', methods=['GET'])
def root():
    return '<<< Tutuka API >>>'
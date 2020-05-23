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
from flaskapp.mongodb import conn
paydnadb = conn.db_init()

from flaskapp.api.tutuka import tutuka_xmlrpc
xml_client = tutuka_xmlrpc.Tutuka_XMLRPC({'terminalID' : env('TerminalID'), 'terminalPassword' : env('TerminalPass')})

bp = Blueprint('tutuka', __name__, url_prefix='/api/tutuka')
CORS(bp)

PROFILES = [{ "name": "sandbox", "profileID": "4731098549"}, { "name": "dummy", "profileID": "1235497356" }]

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

@bp.route('/profilebalance', methods=['GET'])
def get_profilebalance():
    profilename = request.args.get('profilename')
    profile = { k:v for (k,v) in [profile.items() for profile in PROFILES if profile['name'] == profilename][0] }
    print(profile)
    if profile != {}:
        resp = xml_client.profile_balance(profile['name'], get_trans_id())
    # return { 'profile': resp.get('cardNumber'), 'expiryDate': resp.get('expiryDate').value, 'balance': resp.get('balanceAmount'), 'transactionID': resp.get('clientTransactionID') }
    return { 'resp': resp }

@bp.route('/profiles', methods=['GET'])
def get_profiles():
    profiles = []
    for profile in paydnadb.profiles.find({}, {'_id': 0}):
        profiles.append(profile)
    return { "profiles": profiles }

@bp.route('/schemes', methods=['GET'])
def get_schemes():
    schemes = []
    for scheme in paydnadb.schemes.find({}, {'_id': 0}):
        schemes.append(scheme)
    return { "schemes": schemes }

@bp.route('/cards', methods=['GET'])
def get_cards():
    cards = []
    for card in paydnadb.cards.find({}, {'_id': 0}):
        cards.append(card)
    return { "profiles": cards }

@bp.route('/', methods=['GET'])
def root():
    return '<<< Tutuka API >>>'
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

bp = Blueprint('cards', __name__, url_prefix='/api/cards')
CORS(bp)

@bp.route('/', methods=['GET'])
def get_cards():
    cards = []
    for card in paydnadb.cards.find({}, {'authNum': 0}):
        cards.append(card)
    return { "cards": cards }

@bp.route('/<id>', methods=['GET'])
def get_card(id):
    return { "card": paydnadb.cards.find_one({'_id': id}, {'authNum': 0}) }
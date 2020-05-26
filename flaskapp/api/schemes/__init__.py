from flask import (
    Blueprint, render_template, request, url_for, g
)
from flask_cors import CORS

import json, re, os

# logging
from logzero import logger
from flaskapp.api.common import get_trans_id
from envparse import Env

from datetime import datetime

env = Env(
    UserFile=str,
)
env.read_envfile()

from flaskapp.api.common import encrypt_str, decrypt_str

from flaskapp.mongoconnection import db_init
paydnadb = db_init()

bp = Blueprint('schemes', __name__, url_prefix='/api/schemes')
CORS(bp)

def get_scheme_id(name):
    return paydnadb.schemes.find_one({'sysName': name}, {'_id': 1}).get('_id')

def get_scheme_names(id):
    return paydnadb.schemes.find_one({'_id': id}, {'_id': 0, 'sysName': 1, 'viewName': 1})

@bp.route('/', methods=['GET'])
def get_schemes():
    schemes = []
    for scheme in paydnadb.schemes.find({}, {"_id": 0}):
        schemes.append(scheme)
    return { 'schemes': schemes}

@bp.route('/<string:sysname>', methods=['GET'])
def get_scheme(sysname):
    print(sysname)
    schemes = []
    return { 'scheme': paydnadb.schemes.find_one({'sysName': sysname}, {"_id": 0}) }

@bp.route('/<string:sysname>/cards', methods=['GET'])
def get_scheme_cards(sysname):
    schemeId = get_scheme_id(sysname)
    print(schemeId)
    cards = []
    for card in paydnadb.cards.find({'scheme': schemeId}):
        print(card.get('scheme'))
        cards.append(card)
    return { 'cards': cards }

@bp.route('/<int:scheme_id>', methods=['GET'])
def id_to_name(scheme_id):
    return { 'scheme': get_scheme_names(scheme_id)}
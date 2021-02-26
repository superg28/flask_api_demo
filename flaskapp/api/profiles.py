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

# token authentication handling
from flaskapp.auth import jwt_required

# get db connection
from flaskapp.mongoconnection import db_init
paydnadb = db_init()

from flaskapp.api.tutuka import tutuka_xmlrpc
xml_client = tutuka_xmlrpc.Tutuka_XMLRPC({'terminalID' : env('TerminalID'), 'terminalPassword' : env('TerminalPass')})

bp = Blueprint('profiles', __name__, url_prefix='/api/profiles')
CORS(bp)

def pid_to_name(pid):
    return paydnadb.profiles.find_one({'_id': pid}, {'name': 1}).get('name')

def name_to_pid(name):
    return paydnadb.profiles.find_one({'name': name}, {'_id': 1}).get('_id')

@bp.route('/', methods=['GET'])
@jwt_required('super')
def get_profiles():
    profiles = []
    for profile in paydnadb.profiles.find({}):
        profiles.append(profile)
    return { "profiles": profiles }

@bp.route('/<string:name>', methods=['GET'])
@jwt_required('super')
def get_profile(name):
    return { "profile": paydnadb.profiles.find_one({'name': name}, {'_id': 0}) }

@bp.route('/<string:name>/cards', methods=['GET'])
@jwt_required('super')
def get_profile_cards(name):
    profile_cards = [x for x in paydnadb.cards.find({'profile_id': name_to_pid(name)}, {'_id': 1, 'balance': 1})]
    return { "cards": profile_cards }

@bp.route('/id-to-name', methods=['POST'])
def id_to_name():
    print(request.args)
    pid = request.args.get('pid')
    return { 'name': paydnadb.profiles.find_one({'_id': pid}, {'name': 1}).get('name') }
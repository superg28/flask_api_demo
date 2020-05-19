from flask import (
    Blueprint, render_template, request, url_for
)
from flask_cors import CORS

import json
import re

# logging
from logzero import logger
from flaskapp.api.common import get_trans_id
from envparse import Env

env = Env(
    UserFile=str,
    MongoUrl=str,
    MongoUser=str,
    MongoPass=str
)
env.read_envfile()

# DB configs need to go here
from pymongo import MongoClient
mdbclient = MongoClient(env('MongoUrl'), username=env('MongoUser'), password=env('MongoPass'))
paydnadb = mdbclient.payDNA

usersbp = Blueprint('users', __name__, url_prefix='/api/users')
CORS(usersbp)

def field_filter(field_string):
    postal_pattern = re.compile(r'^postal_')
    street_pattern = re.compile(r'^street_')
    postal_match = postal_pattern.match(field_string)
    street_match = street_pattern.match(field_string)

    if street_match:
        return ('street_addr', field_string[street_match.end():])
    elif postal_match:
        return ('postal_addr', field_string[postal_match.end():])
    else:
        return ('', field_string)

# load users
def load_users():
    with open(env('UserFile'), 'r') as fp:
        users = json.load(fp)
    return users

def add_user(user: dict):
    with open(env('UserFile'), 'w') as fp:
        users = json.dump(user, fp, indent=4)

@usersbp.route('/add', methods=['POST'])
def user_add():
    user = {}
    uid = paydnadb.users.count_documents({}) + 1
    user['uid'] = uid
    # default role for all new users
    user['role'] = 'User'
    for field in request.form:
        sub, processedField = field_filter(field)
        value = request.form[field]
        if value != '' and value != 'undefined':
            print(f'{field}: {value}')
        if sub == '':
            user[processedField] = value
        else:
            if user.get(sub):
                if value != 'undefined' and value != '':
                    user[sub][processedField] = value
            else:
                if value != 'undefined' and value != '':
                    user[sub] = {}
                    user[sub][processedField] = value
    print(user)
    resp = paydnadb.users.insert_one(user)
    if resp.inserted_id:
        return { 'resultCode': 0, 'resultText': 'User added successfully'}
    else:
        return { 'resultCode': 255, 'resultText': 'Error adding user'}

@usersbp.route('/', methods=['GET'])
def users():
    return { 'status': 'Users List', 'users': load_users() }

@usersbp.route('/by-id/<int:uid>', methods=['GET'])
def user(uid):
    print(f'URL id: {uid}')
    for user in load_users():
        if user['uid'] == uid:
            return user
    return { 'status': 204, 'message': 'User not found'}

@usersbp.route('/update/<int:uid>', methods=['POST'])
def user_update(uid):
    return '<<< user update >>>'
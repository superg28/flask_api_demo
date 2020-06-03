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

# DB configs need to go here
# from pymongo import MongoClient
# mdbclient = MongoClient(env('MongoUrl'), username=env('MongoUser'), password=env('MongoPass'))
# paydnadb = mdbclient.payDNA

from flaskapp.mongoconnection import db_init
paydnadb = db_init()

bp = Blueprint('users', __name__, url_prefix='/api/users')
# CORS(bp, resources=r'/*')
CORS(bp)

SERVER_PATH_PREFIX = '/home/superg28/projects/paydna-flask-upload-server'

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

def move_files(uid, filepath):
    '''
    move the uploaded (and virus scanned) files to a uid named directory
    :uid the users id assigned on upload
    :file_type determines the folder that gets created
    :filename path of the originally uploaded file
    :return a path to the relocated file for insertion into the database
    '''
    # cast uid to string
    uid = str(uid)
    uidpath = f'user_files/{uid}'
    print(f'uidpath = {uidpath}')
    print(f'Server Path {SERVER_PATH_PREFIX}')
    subdirpath = os.path.join(SERVER_PATH_PREFIX, uidpath)
    print(f'subdirpath: {subdirpath}')
    if not os.path.exists(subdirpath):
        try:
            os.mkdir(subdirpath)
        except:
            print(f'Can\'t create directory, {subdirpath}')
            return

    filename = filepath.split('/')[-1]
    try:
        os.rename(filepath, os.path.join(subdirpath, filename))
    except Exception as err:
        print(f'Error moving file from {filepath} to {os.path.join(subdirpath, filename)}\nError: {err}')

    return os.path.join(uidpath, filename)

def get_uid():
    # returns a managed uid from the database counters
    with paydnadb.counters.find({'_id': 'user_id'}) as cursor:
        uid = cursor.next().get('sequence') + 1
        resp = paydnadb.counters.find_one_and_update({'_id': 'user_id'},{'$inc': {'sequence': 1}})
        print(resp)
    return uid

# load users
def load_users():
    users = []
    for user in paydnadb.users.find({}, {'uid': 1, 'name': 1, 'surname': 1, 'contact_email': 1, 'contact_cell': 1}):
        users.append(user)
    return users

def add_user(user: dict):
    with open(env('UserFile'), 'w') as fp:
        users = json.dump(user, fp, indent=4)

@bp.route('/add', methods=['POST'])
def user_add():
    user = {}
    print(request.headers)
    uid = get_uid()
    user['_id'] = uid
    # default role for all new users
    user['role'] = 'User'
    for field in request.form:
        sub, processedField = field_filter(field)
        value = request.form[field]
        if value != '' and value != 'undefined':
            print(f'{processedField}: {value}')
        if sub == '':
            # move the files to a new uid namespace for the foldername
            if processedField == 'id_document' or processedField == 'poa_document':
                user[processedField] = move_files(uid, decrypt_str(value))
            else:
                user[processedField] = value
        else:
            if user.get(sub):
                if value != 'undefined' and value != '':
                    user[sub][processedField] = value
            else:
                if value != 'undefined' and value != '':
                    user[sub] = {}
                    user[sub][processedField] = value
    user['registered_date'] = datetime.now().strftime('%Y-%m-%d.%H:%M:%S')
    # user['registered_by'] # TODO: add registerer to the user
    print(user)
    resp = paydnadb.users.insert_one(user)
    if resp.inserted_id:
        return { 'resultCode': 0, 'resultText': 'User added successfully'}
    else:
        return { 'resultCode': 255, 'resultText': 'Error adding user'}

@bp.route('/', methods=['GET'])
def users():
    return { 'status': 'Users List', 'users': load_users() }

@bp.route('/<int:uid>', methods=['GET'])
def user(uid):
    print(f'URL id: {uid}')
    if paydnadb.users.count_documents({'_id':uid}) != 0:
        return { 'user': paydnadb.users.find_one({'_id':uid}) }
    return { 'status': 204, 'message': 'User not found'}

@bp.route('/update/<int:uid>', methods=['POST'])
def user_update(uid):
    return '<<< user update >>>'
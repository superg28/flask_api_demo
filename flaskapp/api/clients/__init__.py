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
from flaskapp.mongoconnection import db_init
paydnadb = db_init()

bp = Blueprint('clients', __name__, url_prefix='/api/clients')
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
    :uid the clients id assigned on upload
    :file_type determines the folder that gets created
    :filename path of the originally uploaded file
    :return a path to the relocated file for insertion into the database
    '''
    # cast uid to string
    uid = str(uid)
    uidpath = f'client_files/{uid}'
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
    with paydnadb.counters.find({'_id': 'client_id'}) as cursor:
        uid = cursor.next().get('sequence') + 1
        resp = paydnadb.counters.find_one_and_update({'_id': 'client_id'},{'$inc': {'sequence': 1}})
        print(resp)
    return uid

# load clients
def load_clients():
    clients = []
    for client in paydnadb.clients.find({}, {'uid': 1, 'name': 1, 'surname': 1, 'contact_email': 1, 'contact_cell': 1}):
        clients.append(client)
    return clients

@bp.route('/add', methods=['POST'])
def client_add():
    client = {}
    print(request.headers)
    uid = get_uid()
    client['_id'] = uid
    # default role for all new clients
    client['role'] = 'client'
    for field in request.form:
        sub, processedField = field_filter(field)
        value = request.form[field]
        if value != '' and value != 'undefined':
            print(f'{processedField}: {value}')
        if sub == '':
            # move the files to a new uid namespace for the foldername
            if processedField == 'id_document' or processedField == 'poa_document':
                client[processedField] = move_files(uid, decrypt_str(value))
            else:
                client[processedField] = value
        else:
            if client.get(sub):
                if value != 'undefined' and value != '':
                    client[sub][processedField] = value
            else:
                if value != 'undefined' and value != '':
                    client[sub] = {}
                    client[sub][processedField] = value
    client['registered_date'] = datetime.now().strftime('%Y-%m-%d.%H:%M:%S')
    # client['registered_by'] # TODO: add registerer to the client
    print(client)
    resp = paydnadb.clients.insert_one(client)
    if resp.inserted_id:
        return { 'resultCode': 0, 'resultText': 'client added successfully'}
    else:
        return { 'resultCode': 255, 'resultText': 'Error adding client'}

@bp.route('/', methods=['GET'])
def clients():
    return { 'status': 'Users List', 'clients': load_clients() }

@bp.route('/<int:uid>', methods=['GET'])
def client(uid):
    print(f'URL id: {uid}')
    if paydnadb.clients.count_documents({'_id':uid}) != 0:
        return { 'client': paydnadb.clients.find_one({'_id':uid}) }
    return { 'status': 204, 'message': 'User not found'}

@bp.route('/update/<int:uid>', methods=['POST'])
def client_update(uid):
    return '<<< client update >>>'
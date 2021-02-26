from flask import (
    Blueprint, render_template, request, url_for, abort, make_response
)
from flask_cors import CORS

import json, re
import jwt
from datetime import datetime
from functools import wraps

# logging
from logzero import logger
from flaskapp.api.common import get_trans_id
from envparse import Env

# database connection
from flaskapp import mongoconnection
db = mongoconnection.db_init()

# encryption tools
from flaskapp.api import common

from envparse import Env
env = Env(
    API_JWT_SECRET=str
)

env.read_envfile()

# blueprint setup
bp = Blueprint('auth', __name__, url_prefix='/auth')
CORS(bp)

# jwt required decorator
def jwt_required(role):
    def deco(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            print(request.headers)
            if request.headers.get('authorization'):
                token = request.headers['authorization'].split(' ')[1]
                if check_token(token, role):
                    print('authorized')
                    return f(*args, **kwargs)
                else:
                    abort(403, 'Unauthorized Token')
            else:
                abort(403, 'Tokenless request')
        return wrapper
    return deco


### token helper functions ###
def check_pass(db_password, form_password):
    # challenge password
    if common.decrypt_str(db_password) == form_password:
        return True
    else:
        return False

def check_token(token, role):
    # check the token against the database for the user id in the token
    json_token = decode_token(token)
    if json_token:
        user = db.users.find_one({'_id': json_token.get('user_id')})
        # if user found check token value
        if user and user.get('token') == token and check_role(user.get('role', None), role):
            return True
        else:
            return False
    else:
        return False

def check_role(user_role, token_role):
    if user_role and user_role == token_role:
        print(f'role check on {token_role}')
    return True

def decode_token(token):
    try:
        return jwt.decode(token.encode(), env('API_JWT_SECRET'), algorithms=["HS256"], options={"verify_iat": True})
    except jwt.exceptions.InvalidSignatureError as e:
        print(e)
        return None

def create_token(username, user_id, role):
    return jwt.encode({ 'iat': datetime.utcnow(), 'username': username, 'user_id': user_id, 'role': role}, env('API_JWT_SECRET'), algorithm="HS256", headers={"typ": "JWT", "alg": "HS256"}).decode()

#######################
### Blueprint start ###
#######################
@bp.route('/encode', methods=['GET', 'POST'])
@jwt_required('super')
def encode_token_endp():
    token = jwt.encode({ 'iat': datetime.utcnow(), 'message': 'this is a token'}, env('API_JWT_SECRET'), algorithm="HS256", headers={"typ": "JWT", "alg": "HS256"})
    return { 'token': token.decode()}

@bp.route('/decode', methods=['GET', 'POST'])
@jwt_required('super')
def decode_token_endp():
    token = request.form.get('token')
    decoded_token = decode_token(token)
    return { 'token': decoded_token}

@bp.route('/', methods=['GET', 'POST'])
@jwt_required('super')
def jwt_base():
    print('auth base url')
    return make_response({'resultText': 'this is the JWT base'}), 200

@bp.route('/test', methods=['POST'])
@jwt_required('super')
def jwt_test():
    return make_response({ 'status': 'success'})
    token = request.headers['authorization'].split(' ')[1]
    try:
        return jwt.decode(token, env('API_JWT_SECRET'), algorithms="HS256")
    except jwt.exceptions.InvalidSignatureError as e:
        print(e)
        return 'InvalidSignatureError'

@bp.route('/login', methods=['POST'])
def login():
    for k,v in request.form.items():
        print(f'{k} : {v}')
    user = db.users.find_one({'username': request.form.get('username')})
    if user:
        print(user)
        if check_pass(user.get('password'), request.form.get('password')):
            token = create_token(user.get('username'), user.get('_id'), user.get('role'))
            db.users.update_one({'username': request.form.get('username')}, {'$set': { 'token': token}})
            return make_response({ "user": user.get('username'), "role": user.get('role'), "token": token }), 200
        else:
            return make_response({ "resultCode": 255, "reason": "Password incorrect"})
    else:
        return make_response({ "resultCode": 255, "reason": "Username not found"})

@bp.route('/logout', methods=['POST'])
def logout():
    for k,v in request.form.items():
        print(f'{k} : {v}')
    username = request.form.get('username')
    if username:
        user = db.users.find_one({'username': request.form.get('username')})
        if user and user.get('token', False):
            token = create_token(user.get('username'), user.get('_id'), user.get('role'))
            db.users.update_one({'username': request.form.get('username')}, {'$set': { 'token': ''}})
            return make_response({'status': 'success', 'resultText': f'User, {username}, logged out'}), 200
        else:
            return make_response({ "result": "fail", "reason": "No token found, user is logged out"})
    else:
        return make_response({'status': 'fail', 'resultText': 'No username provided'}), 200

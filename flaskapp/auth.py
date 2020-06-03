from flask import (
    Blueprint, render_template, request, url_for, current_app
)
from flask_cors import CORS

import json, re, jwt
from datetime import datetime

# logging
from logzero import logger
from flaskapp.api.common import get_trans_id
from envparse import Env

from envparse import Env
env = Env(
    API_JWT_SECRET=str
)

env.read_envfile()

bp = Blueprint('auth', __name__, url_prefix='/auth')
CORS(bp)

@bp.route('/encode', methods=['GET', 'POST'])
def encode_token():
    token = jwt.encode({ 'iat': datetime.utcnow(), "typ": "JWT", 'message': 'this is a token'}, env('API_JWT_SECRET'), algorithm="HS256")
    return { 'token': token.decode()}

@bp.route('/decode', methods=['GET', 'POST'])
def decode_token():
    token = ''
    encoded = jwt.encode({ 'iat': datetime.utcnow(), "typ": "JWT", 'message': 'this is a token'}, env('API_JWT_SECRET'), algorithm="HS256")
    jwt.decode(request.args.get('token'))
    return { 'token': encoded}

@bp.route('/', methods=['GET'])
def jwt_base():
    return 'this is the JWT base'

@bp.route('/test', methods=['POST'])
def jwt_test():
    print(request.headers)
    # print(current_app.config)
    token = request.headers['authorization'].split(' ')[1]
    try:
        return jwt.decode(token, 'mysecret', algorithms="HS256")
    except jwt.exceptions.InvalidSignatureError as e:
        print(e)
        return 'InvalidSignatureError'
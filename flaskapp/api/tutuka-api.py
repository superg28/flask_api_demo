from flask import (
    Blueprint, render_template, request, url_for
)
import json

tutukabp = Blueprint('tutuka', __name__, url_prefix='/api/tutuka')

@tutukabp.route('/balance/<string:card>', methods=['GET'])
def get_balance(card):
    return {'balance': '1000', 'cardnumber': card}

@tutukabp.route('/', methods=['GET'])
def root():
    return '<<< Tutuka API >>>'
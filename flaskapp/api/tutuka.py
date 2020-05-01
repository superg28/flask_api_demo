from flask import (
    Blueprint, render_template, request, url_for
)
import json

tutukabp = Blueprint('tutuka', __name__, url_prefix='/api/tutuka')

@tutukabp.route('/balance', methods=['GET'])
def get_balance():
    return {'balance': '1000'}

@tutukabp.route('/', methods=['GET'])
def root():
    return '<<< Tutuka API >>>'
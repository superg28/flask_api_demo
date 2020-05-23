from flask import (
    Blueprint, render_template, request, url_for
)
import json
from random import randint

bp = Blueprint('luhn', __name__, url_prefix='/api/luhn')

# shared functions
def make_cd(non_cd_str):
    doubles = [int(i)*2 if int(i)*2 < 10 else (int(i)*2-9) for i in non_cd_str[::-1][::2]]
    others = [int(i) for i in non_cd_str[::-1][1::2]]
    return str(10 - ((sum(doubles) + sum(others)) % 10))
# 

@bp.route('/', methods=['GET'])
def root():
    return { 'respone': 'Luhn API' }

@bp.route('/check', methods=['GET'])
# def check(numstr):
def check():
    print(request.args)
    numstr = request.args.get('card')
    if numstr:
        doubles = [int(i)*2 if int(i)*2 < 10 else (int(i)*2-9) for i in numstr[::-1][1::2]]
        others = [int(i) for i in numstr[::-1][2::2]]
        # return ((double + other_sum)*9) % 10 == int(numstr[-1])
        return { "card_valid": (10 - ((sum(doubles) + sum(others)) % 10) == int(numstr[-1])) }
    else:
        return { 'status': 'error', 'message': 'Error no card number provided'}

@bp.route('/calc_cd', methods=['GET'])
def api_calc_cd():
    numstr = request.args.get('checkless')
    check_digit = make_cd(numstr)
    return { "check_digit": check_digit, "card_number": numstr + check_digit }

@bp.route('/randomcards', methods=['GET'])
def randomcards():
    prefix = '533892'
    qty =  request.args.get('q')
    cardlist = []
    for _ in range(int(qty)):
        rand_account = str(int(randint(100000001, 999999999)))  
        cardlist.append(prefix + rand_account + make_cd(prefix + rand_account))
    return { "cards": cardlist }

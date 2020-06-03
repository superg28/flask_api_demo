# module of common functions
from datetime import datetime
import re

from envparse import Env
env = Env(
    FernKey=str
)
env.read_envfile()

from cryptography.fernet import Fernet

with open(env('FernKey'), 'rb') as fp:
    key = fp.read()

def get_trans_id():
    return datetime.now().strftime('%Y%m%d%H%M%S.%f')

def find_card(str_to_search):
    bin_regex = r'533892\d{10}'
    find = re.search(bin_regex, str_to_search)
    if find:
        return str_to_search[find.start():find.end()]
    else:
        return 'None'

def get_bool(stringbool):
    if stringbool.lower() == "true":
        return True
    else:
        return False

def encrypt_str(str_to_encrypt):
    # return an encrypted string
    f = Fernet(key)
    return f.encrypt(str_to_encrypt.encode())

def decrypt_str(str_to_decrypt):
    # return a decrypted string
    f = Fernet(key)
    return f.decrypt(str_to_decrypt.encode()).decode()
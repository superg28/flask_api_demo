# module of common functions
from datetime import datetime
import re

def get_trans_id():
    return datetime.now().strftime('%Y%m%d%H%M%S.%f')

def find_card(str_to_search):
    bin_regex = r'533892\d{10}'
    find = re.search(bin_regex, str_to_search)
    if find:
        return str_to_search[find.start():find.end()]
    else:
        return 'None'
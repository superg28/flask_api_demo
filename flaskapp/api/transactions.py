# Handle queing, logging and loading of transactions
from flaskapp import mongoconnection
paydna = mongoconnection.db_init()

# other imports

# Hard configs
TRANS_TYPES = ['LOAD', 'DEDUCT', 'TRANSACTION']

def _get_transaction_id():
    id = paydna.counters.find_one({'_id': 'transaction_id'}).get('sequence')
    paydna.counters.find_one_and_update({'_id': 'transaction_id'}, {"$inc": { "sequence": 1}})
    return id

def log_transaction(card, type, amount, auth_by, trans_id):
    # used to log the transaction once approved
    pass

def add_to_que(card, transaction_type, amount, qued_by):
    # add a transaction to the que for a given card
    return _get_transaction_id()
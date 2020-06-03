# Handle queing, logging and loading of transactions
from flaskapp.mongoconnection import db_init
paydna = db_init()

# other imports

def log_transaction(card, type, amount, auth_by, trans_id):
    # used to log the transaction once approved
    pass

def add_to_que(card, transaction_type, amount, qued_by):
    # add a transaction to the que for a given card
    pass
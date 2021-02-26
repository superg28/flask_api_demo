# Handle queing, logging and loading of transactions
from flaskapp import mongoconnection
paydna = mongoconnection.db_init()

# other imports

# Hard configs
TRANS_TYPES = ['load', 'deduct', 'transfer']

def _get_scheme_load_fee(scheme_id):
    # get the load fee value from the db
    scheme_dets = paydna.schemes.find_one({'_id': scheme_id})
    if scheme_dets:
        return scheme_dets.get('loadFee', 0)
    else:
        return None

def _get_card_dets(card_id):
    # get the card details for traversing
    dets = paydna.cards.find_one({'_id': card_id})
    if dets:
        return dets
    else:
        return None

def _get_transaction_id():
    id = paydna.counters.find_one({'_id': 'transaction_id'}).get('sequence')
    paydna.counters.find_one_and_update({'_id': 'transaction_id'}, {"$inc": { "sequence": 1}})
    return id

def log_transaction(card_number, type, amount, auth_by, trans_id):
    # used to log the transaction once approved
    pass

def load_to_que(card_number, transaction_type, amount, comment, qued_by):
    # add a transaction to the que for a given card
    # get the card details
    card = _get_card_dets(card_number)
    # get a transaction id
    trans_id = _get_transaction_id()
    
    if card != None:
        load_res = paydna.transaction_q.insert_one({'_id': trans_id, 'card': card.get('_id'), 'type': 'load', 'value': amount, 'quedBy': qued_by})
        if load_res:
            # add fee to card here
            # get scheme load fee
            loadFee = _get_scheme_load_fee(card['scheme'])
            feeLoaded = fee_to_que(card_number, trans_id, 'cardLoadFee', loadFee, "load fee associated with trans_id {}".format(trans_id), qued_by)
            if feeLoaded:
                return {'resultCode': 1, 'resultText': 'Load transaction qued, with load fee'}
            else:
                return {'resultCode': 255, 'resultText': 'Error queing loadfee to que'}
        else:
            return {'resultCode': 255, 'resultText': 'Error queing load to the DB'}
    return None

def fee_to_que(card_number, parent_trans, fee_type, amount, comment, qued_by):
    # add an associated fee to a parent transaction
    fee_load_res = paydna.transaction_q.insert_one({})
    if fee_load_res:
        return True
    else:
        return False

def deduct_to_que():
    # add dedutc transaction to the que
    pass

def approve_transaction(trans_id, approved_by, comment):
    # approve a q'd transaction, i.e. process via tutuka API
    pass
import hashlib, hmac
import xmlrpc.client
from datetime import datetime

from logzero import logger

class Tutuka_XMLRPC:

    def __init__(self, config: dict) -> None:
        '''
        Config must be a dictionary with the terminalID and terminal password
        '''
        self.terminalID = config['terminalID']
        self.terminalPassword = config['terminalPassword']
        # self.endPoint = 'https://voucherengine.tutuka.com/handlers/remote/profilexmlrpc.cfm'
        self._endPoint = 'https://vexdev.tutuka.com/handlers/remote/profilexmlrpc.cfm'
        self.xmlc = xmlrpc.client.ServerProxy(self._endPoint)

    def _create_checksum(self, args: list) -> str:
        '''
        returns the necessary checksum, args should be method name and arguments
        '''
        str_list = [str(x) for x in args]
        digester = hmac.new(self.terminalPassword.encode(), ''.join(str_list).encode(), hashlib.sha1)
        # return digester.digest().hex()
        return digester.hexdigest()

    def _date_str(self):
        ''' 
        Return a date string in ISO 8601 datetime format: <dateTime.iso8601>YYYYMMDDTHH:mm:ss<dateTime.iso8601>
        '''
        return xmlrpc.client.DateTime(datetime.utcnow())

    # TUTUKA FUNCTIONS START HERE >>>

    def allocate_card(self, profileID, cardNumber, firstname, lastname, id_passport, cellphone, transactionID):
        '''
        Allocate a card to a bearer
        '''
        method = 'AllocateCard'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, profileID, cardNumber, firstname, lastname, id_passport, cellphone, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.AllocateCard(self.terminalID, profileID, cardNumber, firstname, lastname, id_passport, cellphone, transactionID, transationDate, check_sum)
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except ConnectionRefusedError as err:
            print("Connection Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault))

    def linkcard(self, profileID, cardNumber, transactionID):
        '''
        Link a card to a profile.
        '''
        method = 'LinkCard'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, profileID, cardNumber, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.LinkCard(self.terminalID, profileID, cardNumber, transactionID, transationDate, check_sum)
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except ConnectionRefusedError as err:
            print("Connection Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault))

    def linkcardsbyseqrange(self):
        pass

    def balance(self, profileID, cardNumber, transactionID):
        '''
        returns the balance of a specific card on a profile
        '''
        method = 'Balance'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, profileID, cardNumber, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.Balance(self.terminalID, profileID, cardNumber, transactionID, transationDate, check_sum)
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault))

    def profile_balance(self, profileID, transactionID):
        '''
        returns the balance of a profile
        '''
        method = 'Balance'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, profileID, profileID, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.Balance(self.terminalID, profileID, profileID, transactionID, transationDate, check_sum)
            # print('Card Balance : {}'.format(response))
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault))

    def deduct_card_load_profile(self, profileID, cardNumber, amount: int, transactionID):
        '''
        Deduct requested amount from card and load the amount back to the profile
        '''
        method = 'DeductCardLoadProfile'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, profileID, cardNumber, amount, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.DeductCardLoadProfile(self.terminalID, profileID, cardNumber, amount, transactionID, transationDate, check_sum)
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault))

    def load_card_deduct_profile(self, profileID, cardNumber, amount: int, transactionID):
        '''
        Load a card with the requested amount and deduct the amount off the profile
        '''
        method = 'LoadCardDeductProfile'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, profileID, cardNumber, amount, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.LoadCardDeductProfile(self.terminalID, profileID, cardNumber, amount, transactionID, transationDate, check_sum)
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault))

    def transfer_funds(self, profileID, cardNumberFrom, cardNumberTo, amount: int, transactionID):
        '''
        tranfers funds between 2 cards on a profile
        '''
        method = 'TransferFunds'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, profileID, cardNumberFrom, cardNumberTo, amount, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.TransferFunds(self.terminalID, profileID, cardNumberFrom, cardNumberTo, amount, transactionID, transationDate, check_sum)
            # print('Card Balance : {}'.format(balance))
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault))

    def transfer_profiles(self, profileIDFrom, profileIDTo, amount: int, transactionID):
        '''
        tranfers funds between 2 profiles
        '''
        method = 'TransferFundsBetweenProfiles'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, profileIDFrom, profileIDTo, amount, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.TransferFundsBetweenProfiles(self.terminalID, profileIDFrom, profileIDTo, amount, transactionID, transationDate, check_sum)
            # print('Card Balance : {}'.format(balance))
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault))

    def insert_transaction_fee(self, profileID, cardNumber, fee_type: int, amount: int, transactionID):
        '''
        Deduct requested amount from card as a fee using one of the following (integer) fee type IDs:

        1 - SMS Balance Enquiry
        2 - ATM Balance Enquiry
        3 - ATM Balance Enquiry - Agent Bank
        4 - ATM Cash Withdrawal
        5 - ATM Cash Withdrawal - Agent Bank
        6 - POS Purchase
        7 - POS Purchase with Cashback
        8 - SMS Transaction Notification
        9 - Emergency Cash Advance
        10 - Emergency Card Replacement/Cash Advance
        11 - Cashout
        12 - Card Order
        13 - Card Delivery
        14 - Card Load
        15 - Monthly Active Card
        16 - Monthly Inactive Card
        17 - Non-participating Merchant Fee
        18 - Deposit
        19 - Card Initiation
        20 - Card Reinitiation
        21 - Replacement Card
        22 - Reissue Fee
        23 - SMS PIN Change Fee
        24 - Card To Profile Transfer Fee
        25 - Transfer Fee
        '''
        method = 'InsertTransactionFee'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, profileID, cardNumber, fee_type, amount, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.InsertTransactionFee(self.terminalID, profileID, cardNumber, fee_type, amount, transactionID, transationDate, check_sum)
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault))

    def reverse_transaction_fee(self, profileID, cardNumber, referenceID, reference_date: datetime, transactionID):
        '''
        Reverse a fee that was charged via the API using InsertTransactionFee
        '''
        method = 'ReverseTransactionFee'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, profileID, cardNumber, referenceID, reference_date, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.ReverseTransactionFee(self.terminalID, profileID, cardNumber, referenceID, reference_date, transactionID, transationDate, check_sum)
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault))

    def register(self, emailAddress, password, firstName, lastName, idOrPassportNumber, contactNumber, cellphoneNumber, isCompany, vatNumber, companyName, companyCCNumber, addressLine1, addressLine2, city, postalCode, transactionID):
        '''
        Creates and registers a new profile
        '''
        method = 'Register'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, emailAddress, password, firstName, lastName, idOrPassportNumber, contactNumber, cellphoneNumber, isCompany, vatNumber, companyName, companyCCNumber, addressLine1, addressLine2, city, postalCode, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.Register(self.terminalID, emailAddress, password, firstName, lastName, idOrPassportNumber, contactNumber, cellphoneNumber, isCompany, vatNumber, companyName, companyCCNumber, addressLine1, addressLine2, city, postalCode, transactionID, transationDate, check_sum)
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault))

    def update_profile(self, profileID, emailAddress, password, firstName, lastName, idOrPassportNumber, contactNumber, cellphoneNumber, isCompany, vatNumber, companyName, companyCCNumber, addressLine1, addressLine2, city, postalCode, transactionID):
        '''
        Updates a profile owner's details
        '''
        method = 'UpdateProfile'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, profileID, emailAddress, password, firstName, lastName, idOrPassportNumber, contactNumber, cellphoneNumber, isCompany, vatNumber, companyName, companyCCNumber, addressLine1, addressLine2, city, postalCode, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.UpdateProfile(self.terminalID, profileID, emailAddress, password, firstName, lastName, idOrPassportNumber, contactNumber, cellphoneNumber, isCompany, vatNumber, companyName, companyCCNumber, addressLine1, addressLine2, city, postalCode, transactionID, transationDate, check_sum)
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault))

    def statement(self, profileID, cardNumber, transactionID):
        '''
        returns the statement of a specific card on a profile
        '''
        method = 'Statement'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, profileID, cardNumber, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.Statement(self.terminalID, profileID, cardNumber, transactionID, transationDate, check_sum)
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault))

    def statement_by_date_range(self, profileID, cardNumber, start_date: datetime, end_date: datetime, transactionID):
        '''
        Retrieve the statement of a card over a specified date range.
        '''
        method = 'StatementByDateRange'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, profileID, cardNumber, start_date, end_date, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.StatementByDateRange(self.terminalID, profileID, cardNumber, start_date, end_date, transactionID, transationDate, check_sum)
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault))

    def activate(self, profileID, cardNumber, date_activates: datetime, activation_key, transactionID):
        '''
        Activate a card
        '''
        method = 'Activate'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, profileID, cardNumber, date_activates, activation_key, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.Activate(self.terminalID, profileID, cardNumber, date_activates, activation_key, transactionID, transationDate, check_sum)
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault))
    
    def stop_card(self, profileID, cardNumber, stop_reason: int, transactionID):
        '''
        Stop a card with one of the following allowed (integer) values for stopReasonID:
        1 - Card stopped as it has been lost
        2 - Card stopped as it has been stolen
        3 - Card stopped pending outcome of query
        4 - Card stopped to consolidate onto single card
        5 - Card stopped as it is no longer active
        6 - Card stopped as allowable PIN tries have been exceeded
        7 - Suspected fraud
        8 - Emergency card replacement
        '''
        method = 'StopCard'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, profileID, cardNumber, stop_reason, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.StopCard(self.terminalID, profileID, cardNumber, stop_reason, transactionID, transationDate, check_sum)
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault))

    def update_allocated_card(self, profileID, cardNumber, idOrPassportNumber, cellphone, transactionID):
        '''
        Updates the cellphone or ID number linked to an allocated card.
        '''
        method = 'UpdateAllocatedCard'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, profileID, cardNumber, idOrPassportNumber, cellphone, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.UpdateAllocatedCard(self.terminalID, profileID, cardNumber, idOrPassportNumber, cellphone, transactionID, transationDate, check_sum)
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault))
    

    def status(self, profileID, cardNumber, transactionID):
        '''
        Retrieve the current status of a card
        '''
        method = 'Status'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, profileID, cardNumber, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.Status(self.terminalID, profileID, cardNumber, transactionID, transationDate, check_sum)
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault))

    def cancel_stop_card(self, profileID, cardNumber, transactionID):
        '''
        Un-stop a card
        '''
        method = 'CancelStopCard'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, profileID, cardNumber, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.CancelStopCard(self.terminalID, profileID, cardNumber, transactionID, transationDate, check_sum)
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault))

    def check_authorisation(self, profileID, cardNumber, amount: int, referenceID, reference_date: datetime, transactionID):
        '''
        Provides a method to check if the specified amount was deducted from a card
        '''
        method = 'CheckAuthorisation'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, profileID, cardNumber, amount, referenceID, reference_date, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.CheckAuthorisation(self.terminalID, profileID, cardNumber, amount, referenceID, reference_date, transactionID, transationDate, check_sum)
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault))

    def check_load(self, profileID, cardNumber, amount: int, referenceID, reference_date: datetime, transactionID):
        '''
        Provides a method to check if the specified amount was loaded on a card
        '''
        method = 'CheckLoad'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, profileID, cardNumber, amount, referenceID, reference_date, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.CheckLoad(self.terminalID, profileID, cardNumber, amount, referenceID, reference_date, transactionID, transationDate, check_sum)
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault))

    def set_filtered_state(self):
        '''
        Provides a method to in- or exclude a single voucher from the filtering rules set on a campaign
        '''
        pass
    
    def reset_pin(self, profileID, cardNumber, transactionID):
        '''
        Provides a method to reset the PIN of a card.
        The new PIN is sent to the cardholder by SMS using the cellphone on Tutuka's records
        '''
        method = 'ResetPin'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, profileID, cardNumber, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.ResetPin(self.terminalID, profileID, cardNumber, transactionID, transationDate, check_sum)
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault))

    def set_3d_secure_code(self, profileID, cardNumber, code, transactionID):
        '''
        Provides a method to set the 3DSecure Code of a card.
        The code is being set on Tutuka's card record.
        '''
        method = 'Set3DSecureCode'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, profileID, cardNumber, code, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.Set3DSecureCode(self.terminalID, profileID, cardNumber, code, transactionID, transationDate, check_sum)
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault))

    def delink_card(self, profileID, cardNumber, transactionID):
        '''
        Provides a method to unlink a card from a specified profile.
        This is only possible if the card was never loaded.
        '''
        method = 'DeLinkCard'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, profileID, cardNumber, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.DeLinkCard(self.terminalID, profileID, cardNumber, transactionID, transationDate, check_sum)
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault))

    def update_sms_notification(self, profileID, cardNumber, cellphone, transactionID):
        '''
        Provides a method to change the cellphone number to which SMS notifications are sent or remove it if the value is blank
        '''
        method = 'UpdateSmsNotification'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, profileID, cardNumber, cellphone, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.UpdateSmsNotification(self.terminalID, profileID, cardNumber, cellphone, transactionID, transationDate, check_sum)
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault))
        
    def devalue_profile(self, profileID, cardNumber, amount: int, transactionID):
        '''
        Deducts the requested amount from the Profile specified with a redemption type of “Devalue”
        To deduct the remaining balance from the Profile automatically, specify the amount to be 0 (zero)
        '''
        method = 'DevalueProfile'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, profileID, cardNumber, amount, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.DevalueProfile(self.terminalID, profileID, cardNumber, amount, transactionID, transationDate, check_sum)
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault))

    def create_scheduled_stop(self, profileID, cardNumber, stop_date: datetime, stop_reason: int, stop_comment, transactionID):
        '''
        Schedules the stop of the card on the date of the parameter
        There can only be one active scheduled stop for a card. Will return an error if the schedule already exists
        '''
        method = 'CreateScheduledStop'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, profileID, cardNumber, stop_date, stop_reason, stop_comment, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.CreateScheduledStop(self.terminalID, profileID, cardNumber, stop_date, stop_reason, stop_comment, transactionID, transationDate, check_sum)
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault))

    def update_scheduled_stop(self, profileID, cardNumber, stop_date: datetime, stop_reason: int, stop_comment, transactionID):
        '''
        Schedules the stop of the card on the date of the parameter
        There can only be one active scheduled stop for a card. Will return an error if the schedule already exists
        '''
        method = 'UpdateScheduledStop'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, profileID, cardNumber, stop_date, stop_reason, stop_comment, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.UpdateScheduledStop(self.terminalID, profileID, cardNumber, stop_date, stop_reason, stop_comment, transactionID, transationDate, check_sum)
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault))

    def cancel_scheduled_stop(self, profileID, cardNumber, transactionID):
        '''
        Schedules the stop of the card on the date of the parameter
        There can only be one active scheduled stop for a card. Will return an error if the schedule already exists
        '''
        method = 'CancelScheduledStop'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, profileID, cardNumber, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.CancelScheduledStop(self.terminalID, profileID, cardNumber, transactionID, transationDate, check_sum)
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault)) 

    def get_scheduled_stop(self, profileID, cardNumber, transactionID):
        '''
        Schedules the stop of the card on the date of the parameter
        There can only be one active scheduled stop for a card. Will return an error if the schedule already exists
        '''
        method = 'GetScheduleStopDetail'
        transationDate = self._date_str()
        check_sum = self._create_checksum([method, self.terminalID, profileID, cardNumber, transactionID, transationDate.value])
        
        try:
            response = self.xmlc.GetScheduleStopDetail(self.terminalID, profileID, cardNumber, transactionID, transationDate, check_sum)
            return response
        except xmlrpc.client.ProtocolError as err:
            print("Protocol Error : {}".format(err))
        except xmlrpc.client.Fault as fault:
            print("Fault : {}".format(fault))
        
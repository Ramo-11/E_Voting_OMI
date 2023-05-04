import struct
from utils.Message_Type import MESSAGE
from utils.message_utils import construct_byte_message

class Voter_Signin_Message:
    def __init__(self, username, password):
        self.message_type = MESSAGE.VOTER_SIGNIN.value.to_bytes(1, byteorder='big') 
        self.user_name = username
        self.password = password

    def to_bytes(self):
        base_message = self.message_type + ','.encode() + self.user_name.encode() + ','.encode() + self.password.encode()
        return construct_byte_message(base_message)

class Voter_Registration_Message:
    def __init__(self, voter_id):
        self.message_type = MESSAGE.VOTER_REGISTRATION.value.to_bytes(1, byteorder='big')
        self.election_id = b'\x00\x12\x12\x13\x11\x11\x08\x07\x11\x13\x05\x04\x06\x11\x14\x15'
        self.key_hash = b'\x00' * 64
        self.voter_id = voter_id

    def to_bytes(self):
        base_message = self.message_type + ','.encode() + self.election_id + ','.encode() + self.key_hash + ','.encode() + self.voter_id
        return construct_byte_message(base_message)
    

# this message is responsible for request the collectors information again
class Voter_Heartbeat_Message:
    def __init__(self, voter_id):
        self.message_type = MESSAGE.VOTER_HEARTBEAT.value.to_bytes(1, byteorder='big')
        self.voter_id = voter_id

    def to_bytes(self):
        base_message = self.message_type + ','.encode() + self.voter_id
        return construct_byte_message(base_message)

class Voter_Ballot_Message:
    def __init__(self, ballot, shares):
        self.message_type = MESSAGE.VOTER_BALLOTS.value.to_bytes(1, byteorder='big')
        self.ballot = ballot
        self.shares = shares

    def to_bytes(self):
        base_message = self.message_type + ','.encode() + self.ballot_to_bytes() + ','.encode() + self.shares_to_bytes()
        return construct_byte_message(base_message)
    
    def ballot_to_bytes(self):
        encoded_ballot = b''
        for sublist in self.ballot:
            for value in sublist:
                encoded_ballot += struct.pack('>H', value)

        return encoded_ballot
    
    def shares_to_bytes(self):
        encoded_shares = b''
        for sublist in self.shares:
            for value in sublist:
                encoded_shares += struct.pack('>H', value)
        return encoded_shares
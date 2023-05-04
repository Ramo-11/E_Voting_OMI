from utils.Message_Type import MESSAGE
from utils.collector_utils import generate_random_shares
import struct

class Collector_Message:
    def __init__(self, election_id):
        self.message_type = MESSAGE.COLLECT_STATUS.value.to_bytes(1, byteorder='big')
        self.key_hash = b'\x00' * 64
        self.election_ID = election_id
        self.acceptance = b'\x01'

    def to_bytes(self):
        return self.message_type + ','.encode() + self.key_hash + ','.encode() + self.election_ID + ','.encode() + self.acceptance
    
class Voter_Location_And_Shares:
    def __init__(self):
        self.message_type = MESSAGE.VOTER_LOCATION_AND_SHARES.value.to_bytes(1, byteorder='big')
        self.election_id = b'\x00\x12\x12\x13\x11\x11\x08\x07\x11\x13\x05\x04\x06\x11\x14\x15'
        shares = generate_random_shares()
        self.x = shares[0].to_bytes(2, byteorder='big')
        self.x_prime = shares[1].to_bytes(2, byteorder='big')
        self.location_to_send = 0
        self.sent_first_location = False

    def to_bytes(self):
        location = struct.pack('>f', self.calculate_location())
        return self.message_type + ','.encode() + self.election_id + ','.encode() + location + ','.encode() + self.x + ','.encode() + self.x_prime
    
    def calculate_location(self):
        if self.sent_first_location:
            self.location_to_send += 0.5
        self.sent_first_location = True
        return self.location_to_send
    
    def get_location(self):
        return self.location_to_send
    
    def get_shares(self):
        return [self.x, self.x_prime]
    
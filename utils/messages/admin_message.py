from utils.Message_Type import MESSAGE
from utils import Paillier
from utils.message_utils import construct_byte_message

class Registration_Message:
    def __init__(self, collector_index, pk, pk_length):
        self.message_type = MESSAGE.COLLECTOR_REGISTRATION.value.to_bytes(1, byteorder='big')
        self.election_id = b'\x00\x12\x12\x13\x11\x11\x08\x07\x11\x13\x05\x04\x06\x11\x14\x15'
        self.collector_index = collector_index
        self.pk_length = pk_length.to_bytes(4, byteorder='big')
        self.pk = pk.to_bytes((pk.bit_length() + 7) // 8, byteorder='big')
        self.collector_key_hash = b'\x04' * 64
    
    def to_bytes(self):
        base_message = self.message_type + ','.encode() + self.election_id + ','.encode() + self.collector_index + \
        ','.encode() + self.pk_length + ','.encode() + self.pk + ','.encode() + self.collector_key_hash
        return construct_byte_message(base_message)

import socket

class Metadata_Message:
    def __init__(self, port, m=b'\x03'):
        self.message_type = MESSAGE.OTHER_COLLECTOR_INFO.value.to_bytes(1, byteorder='big')
        self.election_id = b'\x00\x12\x12\x13\x11\x11\x08\x07\x11\x13\x05\x04\x06\x11\x14\x15'
        self.c_host_length = len(socket.gethostbyname('localhost')).to_bytes(4, byteorder='big')
        self.c_host = socket.gethostbyname('localhost').encode()
        self.c_port = port.to_bytes(2, byteorder='big')
        self.c_pk_length = b'\x00' * 4
        self.c_pk = 'my public key'.encode()
        # m is number of candidates
        self.m = m
    
    def to_bytes(self):
        base_message = self.message_type + ','.encode() + self.election_id + ','.encode() + self.c_host_length + \
        ','.encode() + self.c_host + ','.encode() + self.c_port + ','.encode() + self.c_pk_length + \
        ','.encode() + self.c_pk + ','.encode() + self.m
        return construct_byte_message(base_message)
    

class Voter_Registration_Response:
    def __init__(self, m='\x03'):
        self.message_type = MESSAGE.METADATA_VOTER.value.to_bytes(1, byteorder='big')
        self.election_id = b'\x00\x12\x12\x13\x11\x11\x08\x07\x11\x13\x05\x04\x06\x11\x14\x15'
        self.c1_host_length = len(socket.gethostbyname('localhost')).to_bytes(4, byteorder='big')
        self.c1_host = socket.gethostbyname('localhost').encode()
        self.c1_port = 3001
        self.c1_port = self.c1_port.to_bytes(2, byteorder='big')
        self.c1_pk_length = b'\x00' * 4
        self.c1_pk = 'my public key'.encode()
        self.c2_host_length = len(socket.gethostbyname('localhost')).to_bytes(4, byteorder='big')
        self.c2_host = socket.gethostbyname('localhost').encode()
        self.c2_port = 3002
        self.c2_port = self.c2_port.to_bytes(2, byteorder='big')
        self.c2_pk_length = b'\x00' * 4
        self.c2_pk = 'my public key'.encode()
        # m is number of candidates
        self.m = m

    def to_bytes(self):
        base_message = self.message_type + ','.encode() + self.election_id + ','.encode() + self.c1_host_length + \
        ','.encode() + self.c1_host + ','.encode() + self.c1_port + ','.encode() + self.c1_pk_length + \
        ','.encode() + self.c1_pk + ','.encode() + self.c2_host_length + ','.encode() + self.c2_host + ','.encode() + \
        self.c2_port + ','.encode() + self.c2_pk_length + ','.encode() + self.c2_pk + ','.encode() + self.m
        return construct_byte_message(base_message)
    
class Voters_Information:
    def __init__(self, voter1_id, voter2_id, voter3_id):
        self.message_type = MESSAGE.VOTERS_INFO.value.to_bytes(1, byteorder='big')
        self.election_id = b'\x00\x12\x12\x13\x11\x11\x08\x07\x11\x13\x05\x04\x06\x11\x14\x15'
        self.N = b'\x00\x00\x00\x03'
        self.voter1_id = voter1_id
        self.voter2_id = voter2_id
        self.voter3_id = voter3_id
        self.pk_length = b'\x00' * 4
        self.pk = 'my public key'

    def to_bytes(self):
        base_message = self.message_type + ','.encode() + self.election_id + ','.encode() + self.N + \
        ','.encode() + self.voter1_id + ','.encode() + self.voter2_id + ','.encode() + self.voter3_id + \
        ','.encode() + self.pk_length + ','.encode() + self.pk.encode()
        return construct_byte_message(base_message)

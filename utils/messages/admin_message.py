class Registration_Message:
    def __init__(self, message_type, collector_index):
        self.message_type = message_type.value.to_bytes(1, byteorder='big')
        self.election_id = b'\x00\x12\x12\x13\x11\x11\x08\x07\x11\x13\x05\x04\x06\x11\x14\x15'
        self.collector_index = collector_index
        self.pk_length = b'\x00' * 4
        self.pk = 'my public key'
        self.collector_key_hash = b'\x04' * 64
    
    def to_bytes(self):
        return self.message_type + ','.encode() + self.election_id + ','.encode() + self.collector_index + \
        ','.encode() + self.pk_length + ','.encode() + self.pk.encode() + ','.encode() + self.collector_key_hash

import socket

class Metadata_Message:
    def __init__(self, message_type, port):
        self.message_type = message_type.value.to_bytes(1, byteorder='big')
        self.election_id = b'\x00\x12\x12\x13\x11\x11\x08\x07\x11\x13\x05\x04\x06\x11\x14\x15'
        self.c_host_length = len(socket.gethostbyname('localhost')).to_bytes(4, byteorder='big')
        self.c_host = socket.gethostbyname('localhost').encode()
        self.c_port = port.to_bytes(2, byteorder='big')
        self.c_pk_length = b'\x00' * 4
        self.c_pk = 'my public key'.encode()
        # m is number of candidates
        self.m = b'\x05'
    
    def to_bytes(self):
        return self.message_type + ','.encode() + self.election_id + ','.encode() + self.c_host_length + \
        ','.encode() + self.c_host + ','.encode() + self.c_port + ','.encode() + self.c_pk_length + \
        ','.encode() + self.c_pk + ','.encode() + self.m
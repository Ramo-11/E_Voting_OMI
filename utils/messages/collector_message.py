class Collector_Message:
    def __init__(self, message_type, election_id):
        self.message_type = message_type.value.to_bytes(1, byteorder='big')
        self.key_hash = b'\x00' * 64
        self.election_ID = election_id
        self.acceptance = b'\x01'

    def to_bytes(self):
        return self.message_type + ','.encode() + self.key_hash + ','.encode() + self.election_ID + ','.encode() + self.acceptance
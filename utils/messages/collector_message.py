from utils.Message_Type import MESSAGE

class Collector_Message:
    def __init__(self, election_id):
        self.message_type = MESSAGE.COLLECT_STATUS.value.to_bytes(1, byteorder='big')
        self.key_hash = b'\x00' * 64
        self.election_ID = election_id
        self.acceptance = b'\x01'

    def to_bytes(self):
        return self.message_type + ','.encode() + self.key_hash + ','.encode() + self.election_ID + ','.encode() + self.acceptance
    
class Voter_Location:
    def __init__(self):
        self.message_type = MESSAGE.VOTER_LOCATION.value.to_bytes(1, byteorder='big')
        self.election_id = b'\x00\x12\x12\x13\x11\x11\x08\x07\x11\x13\x05\x04\x06\x11\x14\x15'
        self.location = self.calculate_location().to_bytes(1, byteorder='big')

    def to_bytes(self):
        return self.message_type + ','.encode() + self.election_id + ','.encode() + self.location
    
    def calculate_location(self):
        return 5
    
    def get_location(self):
        return self.location
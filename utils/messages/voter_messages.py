from utils.Message_Type import MESSAGE

class Voter_Signin_Message:
    def __init__(self, username, password):
        self.message_type = MESSAGE.VOTER_SIGNIN.value.to_bytes(1, byteorder='big') 
        self.user_name = username
        self.password = password

    def to_bytes(self):
        return self.message_type + ','.encode() + self.user_name.encode() + ','.encode() + self.password.encode()

class Voter_Registration_Message:
    def __init__(self, voter_id):
        self.message_type = MESSAGE.VOTER_REGISTRATION.value.to_bytes(1, byteorder='big')
        self.election_id = b'\x00\x12\x12\x13\x11\x11\x08\x07\x11\x13\x05\x04\x06\x11\x14\x15'
        self.key_hash = b'\x00' * 64
        self.voter_id = voter_id

    def to_bytes(self):
        return self.message_type + ','.encode() + self.election_id + ','.encode() + self.key_hash + ','.encode() + self.voter_id
    

# this message is responsible for request the collectors information again
class Voter_Heartbeat_Message:
    def __init__(self):
        self.message_type = MESSAGE.VOTER_HEARTBEAT.value.to_bytes(1, byteorder='big')

    def to_bytes(self):
        return self.message_type
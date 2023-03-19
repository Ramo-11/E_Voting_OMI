class Collector_Message:
    def __init__(self, message_type, key_hash, election_ID, acceptance):
        self.message_type = message_type
        self.key_hash = key_hash
        self.election_ID = election_ID
        self.acceptance = acceptance

    @classmethod
    def from_bytes(cls, message_bytes):
        message_type = int.from_bytes(message_bytes[:1], byteorder='big')
        key_hash = message_bytes[1:65]
        election_ID = message_bytes[65:81]
        acceptance = int.from_bytes(message_bytes[81:82], byteorder='big')
        return cls(message_type, key_hash, election_ID, acceptance)

    def to_bytes(self):
        message_bytes = len(self.message_type).to_bytes(1, byteorder='big')
        message_bytes += self.key_hash
        message_bytes += self.election_ID
        message_bytes += self.acceptance.to_bytes(1, byteorder='big')
        return message_bytes

class Collector_Message:
    def __init__(self, message_type):
        self.message_type = message_type
        self.key_hash = b'\x00'*64
        self.election_ID = '1234567890123456'
        self.acceptance = 1

    @classmethod
    def from_bytes(cls, message_bytes):
        message_type = int.from_bytes(message_bytes[:1], byteorder='big')
        key_hash = message_bytes[1:65]
        election_ID = message_bytes[65:81]
        acceptance = int.from_bytes(message_bytes[81:82], byteorder='big')
        return cls(message_type, key_hash, election_ID, acceptance)

    def to_bytes(self):
        message_bytes = str(self.message_type.value).encode()
        message_bytes += ",".encode()
        message_bytes += str(self.key_hash).encode()
        message_bytes += ",".encode()
        message_bytes += self.election_ID.encode()
        message_bytes += ",".encode()
        message_bytes += str(self.acceptance).encode()
        return message_bytes

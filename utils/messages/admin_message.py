class Admin_Message:
    def __init__(self, message_type, collector_index):
        self.message_type = message_type
        self.election_ID = '1234567890123456'
        self.collector_index = collector_index
        self.pk_length = 15
        self.pk = 'my public key'
        self.collector_key_hash = 'my collector key hash'
    
    def to_bytes(self):
        message_bytes = str(self.message_type.value).encode()
        message_bytes += ",".encode()
        message_bytes += self.election_ID.encode()
        message_bytes += ",".encode()
        message_bytes += str(self.collector_index).encode()
        message_bytes += ",".encode()
        message_bytes += str(self.pk_length).encode()
        message_bytes += ",".encode()
        message_bytes += self.pk.encode()
        message_bytes += ",".encode()
        message_bytes += self.collector_key_hash.encode()
        return message_bytes
    
    @classmethod
    def from_byte(cls, message_bytes):
        message_type = int.from_bytes(message_bytes[:1], byteorder='big')
        election_ID = message_bytes[1:17]
        collector_index = int.from_bytes(message_bytes[17:18], byteorder='big')
        pk_length = int.from_bytes(message_bytes[18:22], byteorder='big')
        pk = message_bytes[22:22+pk_length]
        collector_key_hash = message_bytes[22+pk_length:]
        return cls(message_type, election_ID, collector_index, pk_length, pk, collector_key_hash)

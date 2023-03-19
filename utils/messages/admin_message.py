class Admin_Message:
    def __init__(self,message_type,election_ID,collector_index,pk_length,pk,collector_key_hash):
        self.message_type = message_type
        self.election_ID = election_ID
        self.collector_index = collector_index
        self.pk_length = pk_length
        self.pk = pk
        self.collector_key_hash = collector_key_hash
    
    def to_bytes(self):
        message_bytes = b''
        message_bytes += len(self.message_type).to_bytes(1, byteorder='big')
        message_bytes += self.message_type.encode('utf-8')
        message_bytes += self.election_ID.encode('utf-8')
        message_bytes += self.collector_index.to_bytes(1, byteorder='big')
        message_bytes += self.pk_length.to_bytes(4, byteorder='big')
        message_bytes += self.pk.encode('utf-8')
        message_bytes += self.collector_key_hash.encode('utf-8')
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

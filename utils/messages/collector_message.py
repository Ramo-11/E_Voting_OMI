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

class LAS_Message:
    def __init__(self, message_type, perm_values,
                 key_hash = b'\x00'*64, 
                 election_id = b'\x00\x12\x12\x13\x11\x11\x08\x07\x11\x13\x05\x04\x06\x11\x14\x15'):
        if len(key_hash) != 64:
            raise ValueError("key_hash must be 64 bytes long")

        if len(election_id) != 16:
            raise ValueError("election_id must be 16 bytes long")

        self.message_type = message_type
        self.key_hash = key_hash
        self.election_id = election_id
        self.perm_values = perm_values
        self.perm_string = self.create_perm_values_string()
    
    def create_perm_values_string(self):
        perm_string = b''
        # Form string of bytes containing the length (4 bytes) and value (0..N-1)
        for perm_value in self.perm_values:
            # Add the length of the value (4 bytes) to the string
            value_length = ((perm_value.bit_length() + 7) // 8)
            value_length_bytes = value_length.to_bytes(4, byteorder='big')
            perm_string += value_length_bytes
            # Add the byte value to the string
            perm_value_bytes = int(perm_value).to_bytes(value_length, byteorder='big')
            perm_string += perm_value_bytes
        return perm_string
    
    def to_bytes(self):
        # Paillier encrypted values are too large to deal with commas (some bytes translate to encoded comma)
        return self.message_type + self.key_hash + self.election_id + self.perm_string


# LAS1 Message: Sent from Collector 1 to Collector 2
class LAS1_Message(LAS_Message):
    def __init__(self, perm_values,
                 key_hash = b'\x00'*64, 
                 election_id = b'\x00\x12\x12\x13\x11\x11\x08\x07\x11\x13\x05\x04\x06\x11\x14\x15',
                 pk_n = b'\x00'):
        super().__init__(MESSAGE.LAS1.value.to_bytes(1, byteorder='big'), perm_values, key_hash, election_id)
        # Find number of bytes of public key n
        pk_n_len_int = ((pk_n.bit_length() + 7) // 8)
        self.pk_n_length = pk_n_len_int.to_bytes(4, byteorder='big')
        self.pk_n = pk_n.to_bytes(pk_n_len_int, byteorder='big')

    def to_bytes(self):
        # No commas, have to parse by lengths
        return self.message_type + self.key_hash + self.election_id + self.pk_n_length + self.pk_n + self.perm_string

class LAS2_Message(LAS_Message):
    def __init__(self, perm_values, 
                 key_hash=b'\x00' * 64, 
                 election_id=b'\x00\x12\x12\x13\x11\x11\x08\x07\x11\x13\x05\x04\x06\x11\x14\x15'):
        super().__init__(MESSAGE.LAS2.value.to_bytes(1, byteorder='big'), perm_values, key_hash, election_id)
from utils.Message_Type import MESSAGE
from utils.message_utils import construct_byte_message
from utils.collector_utils import generate_random_shares

class Collector_Message:
    def __init__(self, election_id):
        self.message_type = MESSAGE.COLLECT_STATUS.value.to_bytes(1, byteorder='big')
        self.key_hash = b'\x00' * 64
        self.election_ID = election_id
        self.acceptance = b'\x01'

    def to_bytes(self):
        base_message = self.message_type + ','.encode() + self.key_hash + ','.encode() + self.election_ID + ','.encode() + self.acceptance
        return construct_byte_message(base_message)
    
class Voter_Location_And_Shares:
    def __init__(self, shares, rji, pk_n):
        self.message_type = MESSAGE.VOTER_LOCATION_AND_SHARES.value.to_bytes(1, byteorder='big')
        self.election_id = b'\x00\x12\x12\x13\x11\x11\x08\x07\x11\x13\x05\x04\x06\x11\x14\x15'
        location_len = ((rji.bit_length() + 7) // 8)
        self.rji = rji.to_bytes(location_len, byteorder='big')
        pk_n_len_int = ((pk_n.bit_length() + 7) // 8)
        self.pk_n_length = pk_n_len_int.to_bytes(4, byteorder='big')
        self.pk_n = pk_n.to_bytes(pk_n_len_int, byteorder='big')
        self.x = shares[0].to_bytes(2, byteorder='big')
        self.x_prime = shares[1].to_bytes(2, byteorder='big')
        self.location_to_send = 0
        self.sent_first_location = False

    def to_bytes(self):
        base_message = self.message_type + self.election_id + self.x + self.x_prime + self.pk_n_length + self.pk_n + self.rji
        return construct_byte_message(base_message)
    
    def get_location(self):
        return self.rji
    
    def get_shares(self):
        return [self.x, self.x_prime]

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
        base_message = self.message_type + self.key_hash + self.election_id + self.perm_string
        return construct_byte_message(base_message)


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
        base_message = self.message_type + self.key_hash + self.election_id + self.pk_n_length + self.pk_n + self.perm_string
        return construct_byte_message(base_message)

class LAS2_Message(LAS_Message):
    def __init__(self, perm_values, r2_values,
                 key_hash=b'\x00' * 64, 
                 election_id=b'\x00\x12\x12\x13\x11\x11\x08\x07\x11\x13\x05\x04\x06\x11\x14\x15'):
        super().__init__(MESSAGE.LAS2.value.to_bytes(1, byteorder='big'), perm_values, key_hash, election_id)
        self.r2_str = b''
        # Form string of bytes containing the length (4 bytes) and value (0..N-1)
        for r2_value in r2_values:
            # Add the length of the value (4 bytes) to the string
            value_length = ((r2_value.bit_length() + 7) // 8)
            value_length_bytes = value_length.to_bytes(4, byteorder='big')
            self.r2_str += value_length_bytes
            # Add the byte value to the string
            perm_value_bytes = int(r2_value).to_bytes(value_length, byteorder='big')
            self.r2_str += perm_value_bytes
    def to_bytes(self):
        # No commas, have to parse by lengths
        base_message = self.message_type + self.key_hash + self.election_id + self.perm_string + self.r2_str
        return construct_byte_message(base_message)
        
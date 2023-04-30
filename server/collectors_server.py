import socket
import threading
import sys
import random
import os
import sys
import time
from random import SystemRandom

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)

from utils.messages.collector_message import Collector_Message, Voter_Location, LAS1_Message, LAS2_Message
from utils.Message_Type import MESSAGE
from utils.Paillier import *
from server.server import Server

class Collector_Server(Server):
    def __init__(self, name, logger, port=3002):
        super().__init__(name, logger, port)
        self.index = None
        self.election_id = None
        self.pk_length = None
        self.pk = None
        self.key_hash = None
        self.other_c_host_length = None
        self.other_c_host = None
        self.other_c_port = None
        self.other_c_pk_length = None
        self.other_c_pk = None
        self.other_collector_sock = None
        self.registered_voters = [False, False, False]
        self.verified_voters = 0
        self.m = None
        self.x = 0
        self.x_prime = 0
        self.pk_n = None
        self.N = 0
        self.paillier = None
        self.las1_buffer = []
        self.las_message_len = None
        self.las2_buffer = []
        self.las2_len = None
        self.r_values = []


    def start(self):
        try:
            self.client_sock.bind((self.server, self.port))
            self.client_sock.listen()
            self.logger.info(f'Server is listening on {self.server}, port {self.port}')
            while True:
                client, address = self.client_sock.accept()
                self.logger.info(f'Connection from: {str(address)}')
                self.thread = threading.Thread(target=self.listen_to_client, args=(client, address))
                self.logger.debug("New thread starting.")
                self.thread.start()
                self.logger.debug(f"New thread started: {self.thread.ident}")
        except:
            self.logger.error(f'Unable to start server')

    def listen_to_client(self, client, address):
        connected = True
        while connected:
            try:
                message = client.recv(int(self.length))
            except:
                break
            message_type = int.from_bytes(message[0:1], byteorder='big')#int.from_bytes(message.split(b',')[0], byteorder='big')
            
            if message == b'':
                continue
            if message_type == MESSAGE.DISCONNECT.value:
                self.logger.info(f'Got a disconnect message from client')
                connected = False
            elif message_type == MESSAGE.GENERATE_SHARES.value:
                encoded_list = [str(s) for s in self.generate_random_shares()]
                final_shares = encoded_list[0] + "," + encoded_list[1]
                client.send(final_shares.encode(self.format))
            elif message_type == MESSAGE.COLLECTOR_REGISTRATION.value:
                self.registration_message_received(message, client)
            elif message_type == MESSAGE.OTHER_COLLECTOR_INFO.value:
                self.collector_information_received(message)
            elif message_type == MESSAGE.VOTER_REGISTRATION.value:
                # register all voters, one by one
                if not self.registered_voters[0] or not self.registered_voters[1] or not self.registered_voters[2]:
                    self.verify_voters_information(message)
                    self.verified_voters += 1
                else:
                    pass
            elif message_type == MESSAGE.VOTERS_INFO.value:
                # admin will send us this message which will contain the voters ids
                self.voters_information_received(message)
            elif message_type == MESSAGE.VOTER_HEARTBEAT.value:
                if self.registered_voters[0] and self.registered_voters[1] and self.registered_voters[2]:
                    # TODO Resolve Issue: this is run multiple times (run for each thread possibly)
                    # Only want begin_LAS to run once
                    # Only run if collector 2 (protocol says begin with collector 1, but either can start 
                    # and this branch is only reached by collector 2)
                    if self.index == b'\x01':
                        # Send y values (encrypted permuted values) to collector 1
                        self.begin_LAS()
                    #self.send_voter_their_location(client)
                self.logger.debug(f'Received heartbeat, but still waiting for other connections')
            elif message_type == MESSAGE.LAS1.value:
                # Handle split messages
                self.handle_las_message(message, self.las1_buffer, self.calculate_r2_values)
            elif message_type == MESSAGE.LAS2.value:
                # self.calculate_r1_values(message)
                self.handle_las_message(message, self.las2_buffer, self.calculate_r1_values)
            else:
                self.logger.info(f'received unknown message from client, the message: {message}')
                self.logger.info(f'disconnecting client...')
                connected = False
        client.close()
        self.logger.info(f'Connection closed with client: {address}')

    def registration_message_received(self, message, client):
        self.logger.info(f'Received Registration Message from admin')
        message_parts = message.split(b',')
        self.election_id = message_parts[1]
        self.index = message_parts[2]
        self.pk_length = message_parts[3]
        self.pk = message_parts[4]
        self.key_hash = message_parts[5]
        collector_message = Collector_Message(self.election_id)
        collector_message = collector_message.to_bytes()
        client.send(collector_message)
        self.logger.info(f'Sent acceptance response to admin')

    def collector_information_received(self, message):
        self.logger.info(f'Received information about the second collector from admin')
        message_parts = message.split(b',')
        self.other_c_host_length = message_parts[2]
        self.other_c_host = message_parts[3].decode('utf-8')
        self.other_c_port = int.from_bytes(message_parts[4], byteorder='big')
        self.other_c_pk_length = message_parts[5]
        self.other_c_pk = message_parts[6]
        self.connect_to_other_collector()
        self.send_message_to_other_collector()

    def verify_voters_information(self, message):
        """
        Compares voter IDs received from Admin with voter IDs received from voters who are connecting with the collector
        """
        message_parts = message.split(b',')
        voter_id = message_parts[3]
        if voter_id == self.voter1_id :
            self.logger.info(f'voter with id {voter_id} has been registered')
            self.registered_voters[0] = True
        elif voter_id == self.voter2_id :
            self.logger.info(f'voter with id {voter_id} has been registered')
            self.registered_voters[1] = True
        elif voter_id == self.voter3_id :
            self.logger.info(f'voter with id {voter_id} has been registered')
            self.registered_voters[2] = True
        else:
            self.logger.error(f'voters ids mismatch: {voter_id}')

    def voters_information_received(self, message):
        self.logger.info(f'Got the voters IDs from admin')
        message_parts = message.split(b',')
        self.N = message_parts[2]
        self.voter1_id = message_parts[3]
        self.voter2_id = message_parts[4]
        self.voter3_id = message_parts[5]

    def connect_to_other_collector(self):
        self.other_collector_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.other_collector_sock.connect((self.other_c_host, self.other_c_port))
        self.logger.info(f'Collector on port {self.port} connected to collector on port {self.other_c_port}')
        #self.send_message_to_other_collector(message)

    def send_message_to_other_collector(self, message=b'\x07'):
        self.logger.debug(f"Sending message to other collector: {message}")
        self.other_collector_sock.sendall(message)
        self.logger.info(f'sent message to other collector')
    
    def split_message(self, message, max_segment_size=991):
        segments = []
        message_len = len(message)
        message_type = message[0:1]
        # Split the message into segments of the desired size or less
        # Max seg size of 991bytes = 1000bytes - 1 for message type - 4 for message length - 4 for seq number
        for i in range(0, len(message), max_segment_size):
            segment = message[i:i+max_segment_size]
            segments.append(segment)
        first_seg = segments[0]
        # Add message length and sequence number (0) to segment
        segments[0] = first_seg + int(message_len).to_bytes(4, "big") + int(0).to_bytes(4, "big")
        for i in range(1,len(segments)):
            # Add message type and sequence number to remaining segments
            segments[i] = message_type + segments[i] + int(i).to_bytes(4, "big")
        return segments
    
    def reconstruct_message(self, segments):
        # Strip sequence number, message length from end of first message
        message = b''
        first_seg = segments.pop(0)[0:-8]
        message += first_seg

        # Remove message type and sequence number
        for segment in segments:
            message += segment[1:-4]
        
        return message

    def generate_random_shares(self):
        random.seed(self.port)

        num_list = list(range(-200, 1500))

        random_nums = random.sample(num_list, 2)

        self.x = int(random_nums[0])
        self.x_prime = (random_nums[1])

        return [self.x, self.x_prime]
    
    def begin_LAS(self):
        self.logger.info("Beginning Paillier")
        self.paillier = initialize_paillier()
        self.pk_n = self.paillier.get_pubkey()
        # Permute values 0..N-1
        voter_locs = random.sample(range(int.from_bytes(self.N, 'big')), int.from_bytes(self.N, 'big'))
        self.logger.debug(f"C2 Permutation: {voter_locs}")
        encrypted_locs = []
        for loc in voter_locs:
            cipher_loc = self.paillier.encrypt(loc, self.pk_n)
            encrypted_locs.append(cipher_loc)
        self.logger.debug(f"C2 Encrypted perm: {encrypted_locs}")
        las1_message = LAS1_Message(encrypted_locs, pk_n=self.pk_n)
        self.logger.info(f"LAS1 message created")
        las1_message = las1_message.to_bytes()
        message_len = len(las1_message)
        self.logger.debug(f"LAS1 msg length: {message_len}")
        # Message may be too long to send as one message, so split
        las1_msg_segments = self.split_message(las1_message)
        self.logger.debug(f"LAS1 message to be sent: {las1_message}")
        self.logger.info("Begin connection to C1...")
        self.connect_to_other_collector()
        for segment in las1_msg_segments:
            self.logger.debug(f"LAS1 msg segment to be sent: {segment}")
            self.send_message_to_other_collector(segment)
    
    def calculate_r2_values(self, message):
        self.logger.info(f"Calculating r2 and z vals on {self.name}")
        # Message type, key hash, election id, public key n length, 
        message_parts = [message[0:1], message[1:65], message[65:81], message[81:85]]
        message_len = len(message)
        self.logger.debug(f"r2 message_len: {message_len}")
        pk_n_length = int.from_bytes(message_parts[3], 'big')
        pk_n_byte_range = 85 + pk_n_length
        self.pk_n = int.from_bytes(message[85:pk_n_length], 'big')
        self.logger.debug(f"pk_n value from message: {self.pk_n}")
        self.N = 3
        val_lengths = []
        vals = []
        sr = SystemRandom()
        # Parse values from message
        if message_len >= pk_n_byte_range+1:
            i = pk_n_byte_range
            while i+1 < message_len-1:
                self.logger.debug(f"i: {i}")
                val_len_byte_start = i
                # Find length (how many bytes) the value is
                val_len_byte_end = val_len_byte_start + 4
                val_len = int.from_bytes(message[val_len_byte_start:val_len_byte_end], 'big')
                i = val_len_byte_end + val_len
                val = int.from_bytes(message[val_len_byte_end:i], 'big')
                self.logger.debug(f"val: {val}")
                vals.append(val)
            # for i in range(pk_n_byte_range, message_len, ):
            #     val_lengths.append(int.from_bytes(message_parts[i], 'big'))
            # for i in range(6, message_len, 2):
            #     vals.append(int.from_bytes(message_parts[i], 'big'))
            r2_values = [sr.randrange(self.pk_n) for _ in range(3)]#random.sample(range(self.pk_n), 3)#int.from_bytes(self.N, 'big'))
            self.logger.debug(f"On {self.port} r2 values: {r2_values}")
            # Send r values to voters at a later point
            self.r_values = r2_values
            reperm_vals = random.sample(vals, len(vals))
            self.logger.debug(f"On {self.port} new permutation: {reperm_vals}")
            encoded_reperm_vals = []
            pk_n_sq = self.pk_n**2
            self.logger.debug(f"On {self.port} pk_n_sq: {pk_n_sq}")
            # Create z values to be sent. r1 values calculated from z values
            self.logger.debug(f"Reperm_vals len: {len(reperm_vals)}")
            self.logger.debug(f"R2_vals len: {len(r2_values)}")
            for i in range(len(reperm_vals)):
                encrypted_r2 = Paillier.encrypt(m=r2_values[i], pubkey=self.pk_n)
                self.logger.debug(f"r2_{i} encrypted: {encrypted_r2}")
                E_inv = inverse(encrypted_r2, pk_n_sq)
                self.logger.debug(f"r2_{i} encrypted inverse: {E_inv}")
                y_2_i = reperm_vals[i] % pk_n_sq
                self.logger.debug(f"y2_{i} mod pk_n_sq: {y_2_i}")
                self.logger.debug(f"z_{i} final value: {y_2_i*E_inv}")
                encoded_reperm_vals.append(y_2_i*E_inv)
            # Send z values to be decrypted
            las2_message = LAS2_Message(encoded_reperm_vals)
            self.logger.info(f"LAS2 message created")
            las2_message = las2_message.to_bytes()
            # Message may be too long to send as one message, so split
            las1_msg_segments = self.split_message(las2_message)
            self.logger.debug(f"LAS2 message to be sent: {las2_message}")
            self.logger.info("Begin connection to C2...")
            self.connect_to_other_collector()
            for segment in las1_msg_segments:
                self.logger.debug(f"LAS2 msg segment to be sent: {segment}")
                self.send_message_to_other_collector(segment)
        else:
            print("No values given")
    
    def calculate_r1_values(self, message):
        # Message type, key hash, election id
        message_parts = [message[0:1], message[1:65], message[65:81]]
        self.logger.debug(f"message_parts: {message_parts}")
        message_len = len(message)
        self.logger.debug(f"r1 message_len: {message_len}")
        key_hash = message_parts[1]
        election_id = message_parts[2]
        val_lengths = []
        vals = []

        # Parse values
        if message_len >= 82:
            i = 81
            while i+1 < message_len:
                self.logger.debug(f"i: {i}")
                val_len_byte_start = i
                val_len_byte_end = val_len_byte_start + 4
                val_len = int.from_bytes(message[val_len_byte_start:val_len_byte_end], 'big')
                i = val_len_byte_end + val_len
                val = int.from_bytes(message[val_len_byte_end:i], 'big')
                self.logger.debug(f"val: {val}")
                vals.append(val)
            # for i in range(3, message_len, 2):
            #     val_lengths.append(int.from_bytes(message_parts[i], 'big'))
            # for i in range(4, message_len, 2):
            #     vals.append(int.from_bytes(message_parts[i], 'big'))
            r1_values = []
            for val in vals:
                r1_values.append(self.paillier.decrypt(val, self.paillier.privkey, self.pk_n))
            self.logger.debug(f"r1 vals: {r1_values}")
            self.r_values = r1_values
        else:
            print("No values given")
    
    def handle_las_message(self, message, message_buffer, r_value_method):
        seq_num = int.from_bytes(message[-4:], "big")
        message_buffer.insert(seq_num, message)
        if seq_num == 0:
            # Ceiling division of total message length and max message bytes
            self.las_message_len = -(int.from_bytes(message[-8:-4], "big")//-991)
        if self.las_message_len != None and len(message_buffer) == self.las_message_len:
            reconstructed_message = self.reconstruct_message(message_buffer)
            r_value_method(reconstructed_message)

    def send_voter_their_location(self, client):
        voter_location_message = Voter_Location()
        message_to_send = voter_location_message.to_bytes()
        self.logger.debug(f'about to send voter their location: {message_to_send}')
        client.sendall(message_to_send)
        self.logger.info(f'Performed LAS and sent voters location')
        self.logger.debug(f'Location sent: {voter_location_message.get_location()}')

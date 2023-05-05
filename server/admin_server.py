import os
import sys
import threading
import time
import struct 

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)

from utils.messages.admin_message import Voter_Registration_Response, Voters_Information
from server.server import Server
from utils.Message_Type import MESSAGE

class Admin_Server(Server):
    def __init__(self, name, logger, port=3002):
        super().__init__(name, logger, port)
        self.users = {
            'user1': 'aaaa',
            'user2': 'bbbb',
            'user3': 'cccc',
        }
        self.N = 3
        self.conn_num = 0
        self.voter_ids = []
        self.key_hashes = []
        self.sent_collectors_and_voters_all_info = False
        self.ballots = [0, 0, 0]
        self.ballots_prime = [0, 0, 0]
        self.vote_tally = {}
        self.M = 3
        num_ques = 3
        tally_len = self.M * num_ques
        self.tallies = [0]*tally_len
        self.ballots_recvd = 0

    def start(self):
        try:
            self.client_sock.bind((self.server, self.port))
            self.client_sock.listen()
            self.logger.info(f'Server is listening on {self.server}, port {self.port}')
            while True:
                client, address = self.client_sock.accept()
                self.logger.debug(f'New Connection from: {str(address)}')
                self.thread = threading.Thread(target=self.listen_to_client, args=(client, address))
                self.thread.start()
        except:
            self.logger.error(f'Unable to start server')

    def listen_to_client(self, client, address):
        connected = True
        while connected:
            try:
                length_prefix = client.recv(4)
                if length_prefix != b'':
                    self.logger.debug(f"Len prefix: {length_prefix}")
                message_len = int.from_bytes(length_prefix, "big")
                if message_len != 0:
                    self.logger.debug(f"Len: {message_len}")
                message = b''
                if message_len > self.length:
                    # Loop until all message data is received
                    while len(message) < message_len:
                        # Determine amount of data to receive in this iteration
                        remaining_len = message_len - len(message)
                        chunk_size = self.length if remaining_len > self.length else remaining_len
                        # Receive data and append to buffer
                        chunk = client.recv(chunk_size)
                        message += chunk
                else:
                    message = client.recv(message_len)
            except:
                break
            message_type = int.from_bytes(message.split(b',')[0], byteorder='big')
            if message == b'':
                continue
            if message_type == MESSAGE.DISCONNECT.value:
                connected = False
            elif message_type == MESSAGE.VOTER_SIGNIN.value:
                self.log_user_in(message)
            elif message_type == MESSAGE.VOTER_REGISTRATION.value:
                self.extract_voters_registration_message(message)
                self.conn_num += 1
                if self.conn_num == self.N:
                    self.send_voters_info_to_collector()
                    time.sleep(5)
                    self.send_collectors_info_to_voters(client, address)
                    self.sent_collectors_and_voters_all_info = True
            elif message_type == MESSAGE.VOTER_HEARTBEAT.value:
                if self.conn_num == 3 and self.sent_collectors_and_voters_all_info:
                    self.send_collectors_info_to_voters(client, address)
                else:
                    self.logger.debug(f'Have not sent voters info to collectors yet')
            elif message_type == MESSAGE.VOTER_BALLOTS.value:
               self.extract_voter_ballot(message)
               self.calculate_total_ballots(self.latest_received_ballot)
               self.tally_votes(message) 
               self.ballots_recvd += 1
               if self.ballots_recvd == self.N:
                   self.display_election_results()
            
        client.close()
        self.logger.debug(f'Connection closed with client: {address}')
            
    def send_collectors_info_to_voters(self, client, address):
        message = Voter_Registration_Response(m=self.M.to_bytes(1, byteorder='big'))
        client.send(message.to_bytes())
        self.logger.info(f'Admin sent collectors inforamtion to voter in address: {address}')

    def send_voters_info_to_collector(self):
        # all voters have successfuly registered
        admin_message = Voters_Information(self.voter_ids[0], self.voter_ids[1], self.voter_ids[2])
        admin_message = admin_message.to_bytes()
        self.logger.debug(f'voters info to be sent to collectors: {admin_message}')
        
        self.connect(port=3001)
        self.send_message(admin_message)
        self.logger.info(f'Sent collector on port 3001 voters information')
        self.close_connection()

        self.connect(port=3002)
        self.send_message(admin_message)
        self.logger.info(f'Sent collector on port 3002 voters information')
        self.close_connection()

    def extract_voters_registration_message(self, message):
        message_parts = message.split(b',')
        self.key_hashes.append(message_parts[2])
        self.voter_ids.append(message_parts[3])
        self.logger.info(f'Admin received voter\'s registration request for voter {message_parts[3]}')

    def extract_voter_ballot(self, message):
        message_parts = message.split(b',')
        #message_parts[1]
        unpacked_data = []
        for i in range(0, len(message_parts[1]), 2):
            value = struct.unpack('>H', message_parts[1][i:i+2])[0]
            unpacked_data.append(value)

        # Convert the list of integers to a list of lists
        self.latest_received_ballot = [[unpacked_data[i], unpacked_data[i+1]] for i in range(0, len(unpacked_data), 2)]
        self.logger.info(f'received ballot from user {self.latest_received_ballot}')

    def log_user_in(self, message):
        self.logger.info(f'Admin received voter\'s sign in request')
        message_parts = message.split(b',')
        username = message_parts[1].decode()
        password = message_parts[2].decode()
        if self.is_user_valid(username, password):
            self.logger.info(f'user {username} has been signed in')

    def is_user_valid(self, username, password):
        if username in self.users and self.users[username] == password:
            return True
        self.logger.info(f'unable to sing user is with username: {username} and password: {password}')
        return False
    
    def calculate_total_ballots(self, ballot):
        self.ballots[0] += ballot[0][0]
        self.ballots[1] += ballot[1][0]
        self.ballots[2] += ballot[2][0]

        self.ballots_prime[0] += ballot[0][1]
        self.ballots_prime[1] += ballot[1][1]
        self.ballots_prime[2] += ballot[2][1]

        print(f'aggregate ballots (p) for question 1 = {self.ballots[0]}')
        print(f'aggregate ballots (p_prime) for question 1 = {self.ballots_prime[0]}')

        print(f'aggregate ballots (p) for question 2 = {self.ballots[1]}')
        print(f'aggregate ballots (p_prime) for question 2 = {self.ballots_prime[1]}')

        print(f'aggregate ballots (p) for question 3 = {self.ballots[2]}')
        print(f'aggregate ballots (p_prime) for question 3 = {self.ballots_prime[2]}')
    
    def tally_votes(self, message):
        vote_vec_len = self.N * self.M
        p_is = []
        xs = []
        message_parts = message.split(b',')
        #message_parts[1]
        unpacked_data = []
        for i in range(0, len(message_parts[2]), 2):
            value = struct.unpack('>H', message_parts[2][i:i+2])[0]
            unpacked_data.append(value)

        # Convert the list of integers to a list of lists
        shares = [[unpacked_data[i], unpacked_data[i+1]] for i in range(0, len(unpacked_data), 2)]
        self.logger.info(f'received shares from user {shares}')
        xs.append(shares[0][0])
        xs.append(shares[1][0])

        for ballot in self.latest_received_ballot:
            p_is.append(ballot[0])

        for i in range(len(p_is)):
            vote = p_is[i] - xs[0] - xs[1]
            vote_to_bit = bin(vote)[2:]
            vote_str = '{0:0>{1}}'.format(vote_to_bit, vote_vec_len)
            vote_pos = vote_str.find("1")
            cand_vote_pos = self.M*i + (vote_pos%self.M)
            cur_tally = self.tallies[cand_vote_pos]
            self.tallies[cand_vote_pos] = cur_tally + 1

    
    # #vote1 = ["240","HW1","Andy"]
    def display_election_results(self):
        ques = {
            "What is the best CS class?": ["240", "555", "511"],
            "What is the hardest homework in CSCI 55500?": ["H1", "H2", "H3"],
            "Who is the best professor in the CS department?": ["Xzou", "Kelly", "Andy"]
        }
        key_list = list(ques.keys())
        for i in range(len(ques.keys())):
            results = []
            cur_max_pos = -1
            cur_max_val = -1
            print(f"Results for question \"{key_list[i]}\": ")
            responses = ques[key_list[i]]
            for j in range(len(responses)):
                tally_pos = i*self.M + j
                total = self.tallies[tally_pos]
                if total > cur_max_val:
                    cur_max_pos = j
                    cur_max_val = total
                results.append(total)
                print(f"\t{responses[j]}: {total}")
            if cur_max_val > 1:
                print(f"\tThe winner is {responses[cur_max_pos]} with {results[cur_max_pos]} votes.")
            else:
                print(f"\tAll candidates tied.")

    
        
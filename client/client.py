import socket
import time
import struct

from utils.Message_Type import MESSAGE
from utils.messages.voter_messages import Voter_Registration_Message, Voter_Heartbeat_Message

class Client:
    def __init__(self, id, logger):
        self.voting_vector = {
            "What is the best CS class?": ["240", "555", "511"],
            "What is the hardest homework in CSCI 55500?": ["H1", "H2", "H3"],
            "Who is the best professor in the CS department?": ["Xzou", "Kelly", "Andy"]
        } 
        self.server = socket.gethostbyname('localhost')
        self.header = 64
        self.format = 'utf-8'
        self.length = 1000
        self.id = id
        self.logger = logger
        self.location = 0
        self.location_tracker = 0
        self.all_shares = []
        self.all_ballots = []
    
    def start_channel_with_admin(self, port):
        self.admin_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.admin_sock.connect((self.server, int(port)))

    def start_channel_with_collector1(self, port):
        self.c1_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.c1_sock.connect((self.server, int(port)))

    def start_channel_with_collector2(self, port):
        self.c2_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.c2_sock.connect((self.server, int(port)))

    def send_message(self, message, sock):
        time.sleep(0.1)
        sock.sendall(message)

    def receive_message_from_admin(self):
        timeout = 2
        message = None
        self.admin_sock.settimeout(timeout)
        try:
            message = self.admin_sock.recv(int(self.length))
            while message == b'':
                message = self.admin_sock.recv(int(self.length))
        except:
            self.logger.debug(f'No message received within {timeout} seconds, sending heartbeat...')
            voter_heartbeat_message = Voter_Heartbeat_Message()
            self.send_message(voter_heartbeat_message.to_bytes(), self.admin_sock)
            self.receive_message_from_admin()
        if message:
            message_type = int.from_bytes(message.split(b',')[0], byteorder='big')
            # receive collectors information from the admin
            if message_type == MESSAGE.METADATA_VOTER.value:
                self.logger.info(f'Received collectors information.')
                self.logger.debug(f'closing connection with admin.')
                self.close_connection(self.admin_sock)
                self.extract_collectors_information(message)
                return
            else:
                self.logger.error(f'Received unknown messge from admin: {message}')

    def receive_message_from_collector(self, sock):
        timeout = 2
        message = None
        sock.settimeout(timeout)
        try:
            message = sock.recv(int(self.length))
            while message == b'':
                message = sock.recv(int(self.length))
        except:
            self.logger.debug(f'No message received within {timeout} seconds, sending heartbeat...')
            voter_heartbeat_message = Voter_Heartbeat_Message()
            self.send_message(voter_heartbeat_message.to_bytes(), sock)
            self.receive_message_from_collector(sock)
        if message:
            message_type = int.from_bytes(message.split(b',')[0], byteorder='big')
            if message_type == MESSAGE.VOTER_LOCATION_AND_SHARES.value:
                self.logger.debug(f'Received location from collector: {message}')
                self.extract_location_and_shares(message)  
                self.location_tracker += 1
                if self.location_tracker == 2:
                    self.location = int(self.location)
                    self.logger.info(f'location = {self.location}')
                    self.start_voting()
            else:
                self.logger.error(f'Received unknown messge from collector: {message}')

    def extract_collectors_information(self, message):
        message_parts = message.split(b',')
        self.election_id = message_parts[1].decode()
        self.c1_host = message_parts[3].decode()
        self.c1_port = int.from_bytes(message_parts[4], byteorder='big')
        self.c1_pk_length = message_parts[5].decode()
        self.c1_pk= message_parts[6].decode()
        self.c2_host = message_parts[8].decode()
        self.c2_port = int.from_bytes(message_parts[9], byteorder='big')
        self.c2_pk_length = message_parts[10].decode()
        self.c2_pk = message_parts[11].decode()
        self.m = message_parts[12].decode()

    def extract_location_and_shares(self, message):
        message_parts = message.split(b',')
        self.location += struct.unpack('>f', message_parts[2])[0]
        x = int.from_bytes(message_parts[3], byteorder='big')
        x_prime = int.from_bytes(message_parts[4], byteorder='big')
        self.all_shares.append([x, x_prime])
        self.logger.info(f'shares: x = {x}, x_prime = {x_prime}')

    def start_voting(self):
        print(list(self.voting_vector.keys())[0])
        print(list(self.voting_vector.values())[0])
        q1_answer = input("")
        if q1_answer not in list(self.voting_vector.values())[0]:
            raise Exception("Answer is not in the list")
        print(list(self.voting_vector.keys())[1])
        print(list(self.voting_vector.values())[1])
        q2_answer = input("")
        if q2_answer not in list(self.voting_vector.values())[1]:
            raise Exception("Answer is not in the list")
        print(list(self.voting_vector.keys())[2])
        print(list(self.voting_vector.values())[2])
        q3_answer = input("")
        if q3_answer not in list(self.voting_vector.values())[2]:
            raise Exception("Answer is not in the list")
        # this is the vote to send in the voter message to send to admin in order for admin to display the winner
        vote = q1_answer + ',' + q2_answer + ',' + q3_answer
        voting_vector = self.generate_voting_vector(vote)
        self.logger.debug(f'voting vector: {voting_vector}')
        self.generate_all_ballots(voting_vector, self.all_shares)
        self.logger.info(f'Ballots = {self.all_ballots}')
    
    def generate_voting_vector(self, vote):
        vector = '000000000'
        voting_list = []
        for i in range(len(list(self.voting_vector.keys()))):
            q_vote = vote.split(',')[i]
            q = list(self.voting_vector.values())[i]
            answer_index = q.index(q_vote) + (3 * self.location)
            vector_list = list(vector)
            vector_list[answer_index] = '1'
            new_vector = ''.join(vector_list)
            v = int(new_vector, 2)
            v_prime = int(new_vector[::-1], 2)
            voting_list.append([v, v_prime]) 
        return voting_list
    
    def generate_all_ballots(self, vote, shares):
        for v in vote:
            p = self.generate_ballots(v[0], shares[0][0], shares[1][0])
            p_prime = self.generate_ballots(v[1], shares[0][1], shares[1][0])
            self.all_ballots.append([p, p_prime])

    def generate_ballots(self, vote, x, x_prime):
        return vote + x + x_prime

    def close_connection(self, sock):
        disconnect_message = MESSAGE.DISCONNECT.value.to_bytes(1, byteorder='big')
        self.send_message(disconnect_message, sock)
        time.sleep(0.1)
        sock.close()
        self.logger.debug('Connection closed successfully.')

    def connect_with_collector2(self):
        self.logger.info(f'Establishing a connection with collector 2 and sending it a registration request')
        self.start_channel_with_collector2(self.c2_port)
        message = Voter_Registration_Message(self.id)
        self.send_message(message.to_bytes(), self.c2_sock)

    def connect_with_collector1(self):
        self.logger.info(f'Establishing a connection with collector 1 and sending it a registration request')
        self.start_channel_with_collector1(self.c1_port)
        message = Voter_Registration_Message(self.id)
        self.send_message(message.to_bytes(), self.c1_sock)
        
import os
import sys
import threading
import time

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
        self.voters_num = 3
        self.conn_num = 0
        self.voter_ids = []
        self.key_hashes = []
        self.sent_collectors_and_voters_all_info = False
        self.ballots = 0
        self.ballots_prime = 0

    def start(self):
        try:
            self.client_sock.bind((self.server, self.port))
            self.client_sock.listen()
            self.logger.info(f'Server is listening on {self.server}, port {self.port}')
            while True:
                client, address = self.client_sock.accept()
                self.logger.info(f'New Connection from: {str(address)}')
                self.thread = threading.Thread(target=self.listen_to_client, args=(client, address))
                self.thread.start()
        except:
            self.logger.error(f'Unable to start server')

    def listen_to_client(self, client, address):
        connected = True
        while connected:
            try:
                message = client.recv(int(self.length))
            except:
                break
            message_type = int.from_bytes(message.split(b',')[0], byteorder='big')
            if message == b'':
                continue
            if message_type == MESSAGE.DISCONNECT.value:
                connected = False
            if message_type == MESSAGE.VOTER_SIGNIN.value:
                self.log_user_in(message)
            if message_type == MESSAGE.VOTER_REGISTRATION.value:
                self.extract_voters_registration_message(message)
                self.conn_num += 1
                if self.conn_num == 3:
                    self.send_voters_info_to_collectoor()
                    time.sleep(5)
                    self.send_collectors_info_to_voters(client, address)
                    self.sent_collectors_and_voters_all_info = True
            if message_type == MESSAGE.VOTER_HEARTBEAT.value:
                if self.conn_num == 3 and self.sent_collectors_and_voters_all_info:
                    self.send_collectors_info_to_voters(client, address)
                else:
                    self.logger.debug(f'Have not sent voters info to collectors yet')
        client.close()
        self.logger.info(f'Connection closed with client: {address}')
            
    def send_collectors_info_to_voters(self, client, address):
        message = Voter_Registration_Response()
        client.send(message.to_bytes())
        self.logger.info(f'Admin sent collectors inforamtion to voter in address: {address}')

    def send_voters_info_to_collectoor(self):
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
    
    # def calculate_total_ballots(self, ballot):
    #     ballot = eval(ballot)
    #     self.ballots += ballot[0]
    #     self.ballots_prime += ballot[1]
    #     self.voters_num = self.voters_num - 1
    #     if self.voters_num == 0:
    #         self.logger.info(f'total ballots: {self.ballots}')
    #         self.logger.info(f'total ballots prime: {self.ballots_prime}')
    #     else:
    #         self.logger.info(f'current ballots: {self.ballots}. Waiting on other votes')
        
import os
import sys
import threading

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)

from utils.messages.admin_message import Voter_Registration_Response, Voters_Information
from utils import Message_Type
from server.server import Server

class Admin_Server(Server):
    def __init__(self, port=3002):
        super().__init__(port)
        self.users = {
            'user1': 'aaaa',
            'user2': 'bbbb',
            'user3': 'cccc',
        }
        self.voters_num = 3
        self.conn_num = 0
        self.voter_ids = []
        self.key_hashes = []
        self.collectors_num = 2
        self.ballots = 0
        self.ballots_prime = 0

    def start(self):
        self.client_sock.bind((self.server, self.port))
        self.client_sock.listen()
        print(f'\nServer is listening on {self.server}, port {self.port}')
        while True:
            client, address = self.client_sock.accept()
            self.conn_num += 1
            print(f'\nConnection from: {str(address)}.\nNumber of connections = {self.conn_num}')
            self.thread = threading.Thread(target=self.listen_to_client, args=(client, address))
            self.thread.start()
            if self.conn_num == 3:
                break
        self.thread.join()
        self.send_info_to_collectoor()
            

    def send_info_to_collectoor(self):
        # all voters have successfuly registered
        # admin now sends the metadata to all collectors
        admin_message = Voters_Information(self.voter_ids[0], self.voter_ids[1], self.voter_ids[2])
        admin_message = admin_message.to_bytes()
        
        self.connect(port=3001)
        self.send_message(admin_message)
        self.close_connection()

        self.connect(port=3002)
        self.send_message(admin_message)
        self.close_connection()

    def listen_to_client(self, client, address):
        connected = True
        while connected:
            try:
                message = client.recv(int(self.length))
            except:
                break
            message_type = str(int.from_bytes(message.split(b',')[0], byteorder='big'))
            if message == b'':
                continue
            if message_type == '1':
                connected = False
            if message_type == '7':
                print(f'\nAdmin received voter\'s sign in request')
                message_parts = message.split(b',')
                username = message_parts[1].decode()
                password = message_parts[2].decode()
                if self.is_user_valid(username, password):
                    print(f'user {username} has been signed in')
            if message_type == '8':
                print(f'\nAdmin received voter\'s registration request')
                message_parts = message.split(b',')
                self.key_hashes.append(message_parts[2])
                self.voter_ids.append(message_parts[3])
                message = Voter_Registration_Response()
                client.send(message.to_bytes())
                print(f'Admin sent voter\'s collectors inforamtion\n')
                break
        client.close()
        print(f'Connection closed with client: {address}')
            
    def is_user_valid(self, username, password):
        if username in self.users and self.users[username] == password:
            return True
        print(f'unable to sing user is with username: {username} and password: {password}')
        return False
    
    def calculate_total_ballots(self, ballot):
        ballot = eval(ballot)
        self.ballots += ballot[0]
        self.ballots_prime += ballot[1]
        self.voters_num = self.voters_num - 1
        if self.voters_num == 0:
            print(f'total ballots: {self.ballots}')
            print(f'total ballots prime: {self.ballots_prime}')
        else:
            print(f'current ballots: {self.ballots}. Waiting on other votes')
        
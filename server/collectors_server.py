import socket
import threading
import sys
import random
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)

from utils.messages.collector_message import Collector_Message, Voter_Location
from server.server import Server

class Collector_Server(Server):
    def __init__(self, port=3002):
        super().__init__(port)
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
        self.m = None
        self.x = 0
        self.x_prime = 0

    def start(self):
        self.client_sock.bind((self.server, self.port))
        self.client_sock.listen()
        print(f'\nServer is listening on {self.server}, port {self.port}\n')
        while True:
            client, address = self.client_sock.accept()
            print(f'\nConnection from: {str(address)}')
            self.thread = threading.Thread(target=self.listen_to_client, args=(client, address))
            self.thread.start()

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
            elif message_type == '3':
                encoded_list = [str(s) for s in self.generate_random_shares()]
                final_shares = encoded_list[0] + "," + encoded_list[1]
                client.send(final_shares.encode(self.format))
            elif message_type == '4':
                print(f'\nReceived Registration Message from admin')
                message_parts = message.split(b',')
                self.election_id = message_parts[1]
                self.index = message_parts[2]
                self.pk_length = message_parts[3]
                self.pk = message_parts[4]
                self.key_hash = message_parts[5]
                collector_message = Collector_Message(self.election_id)
                collector_message = collector_message.to_bytes()
                client.send(collector_message)
                print(f'\nSent acceptance response to admin')
            elif message_type == '6':
                print(f'\nReceived information about the second collector from admin')
                message_parts = message.split(b',')
                self.other_c_host_length = message_parts[2]
                self.other_c_host = message_parts[3].decode('utf-8')
                self.other_c_port = int.from_bytes(message_parts[4], byteorder='big')
                self.other_c_pk_length = message_parts[5]
                self.other_c_pk = message_parts[6]
                # print(f'\nhost on port {self.port} received information about the other host on port {self.other_c_port}')
                self.connect_to_other_collector()
            elif message_type == '8':
                # verify voter ID is the same as the one obtained from admin, then voter is officially registered with this collector
                message_parts = message.split(b',')
                voter_id = message_parts[3]
                if not hasattr(self, 'voter1_id') or not hasattr(self, 'voter2_id') or not hasattr(self, 'voter3_id'):
                    try: 
                        if voter_id == self.voter1_id or voter_id == self.voter2_id or voter_id == self.voter3_id:
                            print(f'Verified voter ID: {voter_id}, voter is now registered')
                            message = Voter_Location()
                            self.send_message(message.to_bytes())
                    except:
                        print(f'Verification period ended, did not get voter Ids from Admin')
                else:
                    print(f'Verification failed, voter ID: {voter_id} is not registered with this collector')
                connected = False
                
            # receive voters information from admin
            elif message_type == '10':
                message_parts = message.split(b',')
                self.N = message_parts[2]
                self.voter1_id = message_parts[3]
                self.voter2_id = message_parts[4]
                self.voter3_id = message_parts[5]
                print(f'Got the voters IDs from admin')
                connected = False
            else:
                print(f'\nreceived unknown message from client, the message: {message}\n')
                connected = False
        client.close()
        print(f'\nConnection closed with client: {address}')

    def connect_to_other_collector(self):
        self.other_collector_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.other_collector_sock.connect((self.other_c_host, self.other_c_port))
        print('\nCollector 2 connected to collector 1')
        self.send_message_to_other_collector(b'\x07')

    def send_message_to_other_collector(self, message):
        self.other_collector_sock.sendall(message)
        print(f'\nsent message to collector 1')

    def generate_random_shares(self):
        random.seed(self.port)

        num_list = list(range(-200, 1500))

        random_nums = random.sample(num_list, 2)

        self.x = int(random_nums[0])
        self.x_prime = (random_nums[1])

        return [self.x, self.x_prime]

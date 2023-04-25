import socket
import threading
import sys
import random
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)

from utils.messages.collector_message import Collector_Message, Voter_Location
from utils.Message_Type import MESSAGE
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

    def start(self):
        try:
            self.client_sock.bind((self.server, self.port))
            self.client_sock.listen()
            self.logger.info(f'Server is listening on {self.server}, port {self.port}')
            while True:
                client, address = self.client_sock.accept()
                self.logger.info(f'Connection from: {str(address)}')
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
            elif message_type == MESSAGE.VOTERS_INFO.value:
                # admin will send us this message which will contain the voters ids
                self.voters_information_received(message)
            elif message_type == MESSAGE.VOTER_HEARTBEAT.value:
                if self.registered_voters[0] and self.registered_voters[1] and self.registered_voters[2]:
                    self.send_voter_their_location(client)
                self.logger.debug(f'Received heartbeat, but still waiting for other connections')
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
        self.logger.info('Collector 2 connected to collector 1')
        self.send_message_to_other_collector(b'\x07')

    def send_message_to_other_collector(self, message):
        self.other_collector_sock.sendall(message)
        self.logger.info(f'sent message to other collector')

    def generate_random_shares(self):
        random.seed(self.port)

        num_list = list(range(-200, 1500))

        random_nums = random.sample(num_list, 2)

        self.x = int(random_nums[0])
        self.x_prime = (random_nums[1])

        return [self.x, self.x_prime]

    def send_voter_their_location(self, client):
        voter_location_message = Voter_Location()
        message_to_send = voter_location_message.to_bytes()
        self.logger.debug(f'about to send voter their location: {message_to_send}')
        client.sendall(message_to_send)
        self.logger.info(f'Performed LAS and sent voters location')
        self.logger.debug(f'Location sent: {voter_location_message.get_location()}')

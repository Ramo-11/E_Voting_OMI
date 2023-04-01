import socket
import threading
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)

from utils.messages import admin_message
from utils import Message_Type
from parent_server import Server

class Admin_Server(Server):
    def __init__(self, port=3002):
        super().__init__(port)
        self.voters_num = 3
        self.collectors_num = 2
        self.ballots = 0
        self.ballots_prime = 0
    
    def listen_to_client(self, client, address):
        connected = True
        while connected:
            message = client.recv(int(self.length)).decode(self.format)
            message_type = message.split(',')[0]
            print(f'Message received from client: {message}')
            if message_type == '1':
                print(f'Connection closed with client: {address}')
                connected = False
            elif message_type == '2':
                self.calculate_total_ballots(message)
            elif message_type == '5':
                acceptance = message.split(',')[0]
                if acceptance == '1':
                    if self.collectors_num == 0:
                        print('All collectors accepted')
                    else:
                        self.collectors_num = self.collectors_num - 1
                        print('Collector accepted')
            else:
                print(f'Invalid message received from client: {address}')
                connected = False
        client.close()
    
    def construct_admin_message(self, collector_index):
        message = admin_message.Admin_Message(collector_index)
        return message.to_bytes()

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

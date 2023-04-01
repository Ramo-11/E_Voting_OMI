import socket
import threading
import sys
import random
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)

from utils.messages import collector_message
from utils.messages.collector_message import Collector_Message
from utils import Message_Type
from parent_server import Server

class Collector_Server(Server):
    def __init__(self, port=3002):
        super().__init__(port)
        self.x = 0
        self.x_prime = 0

    def listen_to_client(self, client, address):
        connected = True
        while connected:
            message = client.recv(int(self.length)).decode(self.format)
            message_type = message.split(',')[0]
            print(f'Message received from client: {message}')
            if message_type == '1':
                print(f'Connection closed with client: {address}')
                connected = False
            elif message_type == '3':
                encoded_list = [str(s) for s in self.generate_random_shares()]
                final_shares = encoded_list[0] + "," + encoded_list[1]
                client.send(final_shares.encode(self.format))
            elif message_type == '4':
                collector_message = Collector_Message(Message_Type.MESSAGE.COLLECT_STATUS)
                collector_message = collector_message.to_bytes()
                client.send(collector_message)
            else:
                print(f'Invalid message received from client: {address}')
                connected = False
        client.close()

    def construct_collector_message(self):
        message = collector_message.Collector_Message()
        return message.to_bytes()

    def generate_random_shares(self):
        random.seed(self.port)

        num_list = list(range(-200, 1500))

        random_nums = random.sample(num_list, 2)

        self.x = int(random_nums[0])
        self.x_prime = (random_nums[1])

        return [self.x, self.x_prime]

import socket
import threading
import sys
import random
import time

sys.path.insert(1, '/Users/omar.abdelalim/codespace/E_Voting_OMI')
from utils.messages import collector_message

class Server:
    def __init__(self, port=3002):
        self.x = 0
        self.x_prime = 0
        self.port = port
        self.server = socket.gethostbyname('localhost')
        self.header = 64
        self.format = 'utf-8'
        self.voters_num = 3
        self.ballots = 0
        self.ballots_prime = 0

    def start(self):
        print('Starting Server')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.server, self.port))
        self.sock.listen()
        print(f'Server is listening on {self.server}, port {self.port}')
        while True:
            client, address = self.sock.accept()
            print('Connection from: {}'.format(str(address)))
            self.thread = threading.Thread(target=self.listen_to_client, args=(client, address))
            self.thread.start()
    
    def construct_message(self):
        message_type = 'TYPE_COLLECT_STATUS'
        key_hash = b'\x00'*64
        election_ID = b'\x00'*16
        acceptance = 1
        message = collector_message.Collector_Message(message_type, key_hash, election_ID, acceptance)
        return message.to_bytes()

    def listen_to_client(self, client, address):
        connected = True
        while connected:
            message_length = client.recv(self.header).decode(self.format)
            if message_length:
                message = client.recv(int(message_length)).decode(self.format)
                print(f'Message received from client: {message}')
                if message == 'closing connection':
                    print(f'Connection closed with client: {address}')
                    break;
                if message == 'give me shares':
                    encoded_list = [str(s) for s in self.generateRandomShares()]
                    final_shares = encoded_list[0] + "," + encoded_list[1]
                    client.send(final_shares.encode(self.format))
                if message == 'disconnect':
                    connected = False
                else:
                    self.calculate_total_ballots(message)
        client.close()

    def generateRandomShares(self):
        random.seed(self.port)

        num_list = list(range(-200, 1500))

        random_nums = random.sample(num_list, 2)

        self.x = random_nums[0]
        self.x_prime = random_nums[1]

        return [self.x, self.x_prime]

    def calculate_total_ballots(self, ballot):
        self.ballots += ballot[0]
        self.ballots_prime += ballot[1]
        self.voters_num = self.voters_num - 1
        if self.voters_num == 0:
            print(f'total ballots: {self.ballots}')
            print(f'total ballots prime: {self.ballots_prime}')
        else:
            print(f'current ballots: {self.ballots}. Waiting on other votes')


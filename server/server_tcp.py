import socket
import threading
import sys

sys.path.insert(1, '/Users/omar.abdelalim/codespace/E_Voting_OMI')
from utils.messages import collector_message

class Server:
    def __init__(self, port=3002):
        self.port = port
        self.server = socket.gethostbyname('localhost')
        self.header = 64
        self.format = 'utf-8'

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
                print(f'[{address}]: {message}')
                client.send('Gotcha buddy'.encode(self.format))
                if message == 'disconnect':
                    connected = False
        client.close()

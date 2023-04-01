import socket
import threading
import sys
import random
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)

from utils.messages import admin_message
from utils import Message_Type

class Server:
    def __init__(self, port):
        self.port = port
        self.server = socket.gethostbyname('localhost')
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket = None
        self.length = 1000
        self.format = 'utf-8'

    def start(self):
        print('Starting Server')

        self.client_sock.bind((self.server, self.port))
        self.client_sock.listen()
        print(f'Server is listening on {self.server}, port {self.port}')
        while True:
            client, address = self.client_sock.accept()
            print('Connection from: {}'.format(str(address)))
            self.thread = threading.Thread(target=self.listen_to_client, args=(client, address))
            self.thread.start()

    def is_socket_connected(self, sock):
        try:
            sock.getpeername()
        except socket.error:
            return False
        return True

    def connect(self, port=3001):
        # if the socket doesn't exists and is not connected, connect
        if not self.server_socket or not self.is_socket_connected(self.server_socket):
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.connect((self.server, int(port)))
        else:
            print('Socket is already connected')

    def close_connection(self):
        disconnect_message = Message_Type.MESSAGE.DISCONNECT.value.to_bytes(1, byteorder='big')
        self.send_message(disconnect_message)
        self.server_socket.close()
        print('Connection closed.')

    def send_message(self, message):
        print(f'message to be sent: {message}')
        self.server_socket.send(message)

    def receive_message(self):
        self.server_socket.settimeout(10)
        message = self.server_socket.recv(int(self.length))
        print(f'message received: {message}')
        return message
    
    def listen_to_client(self, client, address):
       pass
            
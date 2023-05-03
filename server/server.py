import socket
import threading
import sys
import time
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)

from utils import Message_Type
from utils import Paillier

class Server:
    def __init__(self, name, logger, port):
        p = Paillier.initialize_paillier()
        self.pk = p.get_pubkey()
        self.pk_length = p.get_keylength()
        self.name = name
        self.port = port
        self.server = socket.gethostbyname('localhost')
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket = None
        self.length = 1000
        self.format = 'utf-8'
        self.logger = logger

    def start(self):
        pass

    def is_socket_connected(self, sock):
        try:
            sock.getpeername()
        except socket.error:
            return False
        return True

    def connect(self, port):
        # if the socket doesn't exists and is not connected, connect
        if not self.server_socket or not self.is_socket_connected(self.server_socket):
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.server_socket.connect((self.server, int(port)))
                self.logger.debug(f'Connected to server on port {port}')
            except:
                self.logger.error(f'Unable to connect, trying again...')
                self.connect(port)
        else:
            self.logger.error('Socket is already connected')

    def close_connection(self):
        disconnect_message = Message_Type.MESSAGE.DISCONNECT.value.to_bytes(1, byteorder='big')
        self.send_message(disconnect_message)
        time.sleep(0.1)
        self.server_socket.close()
        self.logger.debug('Connection closed with server.')

    def send_message(self, message):
        self.server_socket.sendall(message)

    def receive_message(self):
        self.server_socket.settimeout(10)
        message = self.server_socket.recv(int(self.length))
        return message
    
    def listen_to_client(self, client, address):
       pass
            
import socket

class Client:
    def __init__(self):
        self.server = socket.gethostbyname('localhost')
        self.header = 64
        self.format = 'utf-8'
    
    def start(self, port=3002):
        """
        Connect to the server through TCP
        """
        print(f'port: {port}')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.server, int(port)))

    def send_message(self, message):
        """
        Send the length of the message first,
        Then, send the actual message
        """
        message = message.encode(self.format)
        message_length = str(len(message)).encode(self.format)
        message_length += b' ' * (self.header - len(message_length))
        self.sock.send(message_length)
        self.sock.send(message)
        message_from_server = self.sock.recv(self.header).decode(self.format)
        print(f'server says: {message_from_server}')
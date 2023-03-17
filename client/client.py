import socket
import requests
from routes import routes as routes_

from flask import Flask, render_template, redirect, url_for, request, flash, make_response

app = Flask(__name__, template_folder='../templates')
app.config['SECRET_KEY'] = 'mysecretkey'
app.register_blueprint(routes_)

class Client:
    def __init__(self):
        self.port = 3000
        self.server = socket.gethostbyname('localhost')
        self.header = 64
        self.format = 'utf-8'
    
    def start(self):
        """
        Connect to the server
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.server, self.port))

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

def main():
    client = Client()
    client.start()
    another_one = True
    while another_one:
        message = input('Input (q to quit): ')
        if message == 'q':
            another_one = False
            message = 'disconnect'
        client.send_message(message)

if __name__ == '__main__':
    app.run(port=3000, debug=True)
    # main()

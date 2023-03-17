import socket
import requests

# import os
from flask import Flask, render_template, redirect, url_for, request, flash, make_response
# from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user
# from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
token = None

@app.route('/')
def index():
    if 'token' not in request.cookies:
        return redirect(url_for('signup'))
    return redirect(url_for('home'))

@app.route('/home')
def home():
    if 'token' not in request.cookies:
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = {'username': request.form['username'], 'password': request.form['password']}
        response = requests.post('http://localhost:3001/api/login', json=data)
        if response.status_code == 200:
            token = response.json().get('token')
            response = make_response(redirect(url_for('home')))
            response.set_cookie('token', token)
            return response
        else:
            flash(f"Cannot login: {response.json()['error']}")
            return render_template('login.html')
    if 'token' in request.cookies:
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        response = requests.post('http://localhost:3001/api/signup', json={'username': request.form['username'], 'password': request.form['password']})
        if response.status_code == 200:
            return redirect(url_for('home'))
        else:
            flash(f"Cannot signup: {response.json()['error']}")
            return render_template('signup.html')
    if 'token' in request.cookies:
        return redirect(url_for('home'))
    return render_template('signup.html')

@app.route('/logout', methods=['POST'])
def logout():
    token = request.cookies.get('token')
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post('http://localhost:3001/api/logout', headers=headers)
    if response.status_code == 200:
        response = make_response(redirect(url_for('home')))
        response.delete_cookie('token')
        return response
    else:
        flash(f"Unable to logout: {response.json()['error']}")
        return redirect(url_for('home'))

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

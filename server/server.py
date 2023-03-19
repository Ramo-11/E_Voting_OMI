import socket
import threading

from flask import Flask, jsonify, request, make_response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, verify_jwt_in_request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://evoting_user:123456@127.0.0.1/postgres'
app.config['SECRET_KEY'] = 'mysecretkey'
db = SQLAlchemy(app)
socketio = SocketIO(app)

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

    def listen_to_client(self, client, address):
        message_length = client.recv(64).decode(self.format)
        if message_length:
            message = client.recv(int(message_length)).decode(self.format)
            print(f'[{address}]: {message}')
            socketio.emit('message', {'address': str(address), 'message': message})
        client.close()
        print(f'[{address}] disconnected')
        socketio.emit('disconnect', {'address': str(address)})

jwt = JWTManager(app)

# Initialize the login manager
login_manager = LoginManager()
login_manager.init_app(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/api/message', methods=['POST'])
def receive_message():
    message = request.json['message']
    print(f"Received message: {message}")
    return 'OK'

@app.route('/api/login', methods=['POST'])
def login():
    print("herer?")
    if current_user.is_authenticated:
        return jsonify({'success': 'User was successfully logged in.'}), 200
    username = request.json['username']
    password = request.json['password']
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        token = create_access_token(identity=user.id, expires_delta=expires_at - datetime.utcnow())
        return jsonify({'success': 'User was successfully logged in.', 'token': token}), 200
    else:
        return jsonify({'error': 'Unable to log the user in'}), 400

@app.route('/api/signup', methods=['POST'])
def signup():
    username = request.json['username']
    password = request.json['password']
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'error': 'Username already exists.'}), 400
    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'success': 'User was successfully created.'}), 200

@app.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        verify_jwt_in_request()
        logout_user()
        response = make_response(jsonify({'success': 'User was successfully logged out.'}), 200)
        response.set_cookie('token', '', httponly=True)
        return response
    except:
        return jsonify({'error': 'Unable to log user out.'}), 400

if __name__ == '__main__':
    server = Server()
    server_thread = threading.Thread(target=server.start)
    server_thread.start()
    socketio.run(app, port=3001)
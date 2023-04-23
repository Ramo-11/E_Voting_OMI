import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT_DIR)

CLIENT_DIR = os.path.join(ROOT_DIR, 'Client')
sys.path.insert(1, CLIENT_DIR)

from utils.messages.voter_messages import Voter_Signin_Message, Voter_Registration_Message
from client.client import Client

voter2 = Client(b'\x02' * 4)
voter2.start(port=3003)

# send sign in request to admin
print(f'\nSending sign in request to admin')
signin_message = Voter_Signin_Message('user2', 'bbbb')
voter2.send_message(signin_message.to_bytes())

# send registration request to admin
print(f'\nSending registration request to admin')
voter_reigstration_message = Voter_Registration_Message(voter2.id)
voter2.send_message(voter_reigstration_message.to_bytes())

voter2.receive_message()
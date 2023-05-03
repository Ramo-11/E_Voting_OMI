import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT_DIR)

CLIENT_DIR = os.path.join(ROOT_DIR, 'Client')
sys.path.insert(1, CLIENT_DIR)

from utils.messages.voter_messages import Voter_Signin_Message, Voter_Registration_Message
from client.client import Client
from utils.logger_utils import get_logger

logger = get_logger('voter1')

voter1 = Client(b'\x01' * 4, logger)
voter1.start_channel_with_admin(port=3003)

# send sign in request to admin
logger.info(f'Sending sign in request to admin')
signin_message = Voter_Signin_Message('user1', 'aaaa')
voter1.send_message(signin_message.to_bytes(), voter1.admin_sock)

# send registration request to admin
logger.info(f'Sending registration request to admin')
voter_reigstration_message = Voter_Registration_Message(voter1.id)
voter1.send_message(voter_reigstration_message.to_bytes(), voter1.admin_sock)

voter1.receive_message_from_admin()


voter1.connect_with_collector2()
voter1.receive_message_from_collector(voter1.c2_sock)
# voter1.close_connection(voter1.c2_sock)

voter1.connect_with_collector1()
voter1.receive_message_from_collector(voter1.c1_sock)
# voter1.close_connection(voter1.c1_sock)

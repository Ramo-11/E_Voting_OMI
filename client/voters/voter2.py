import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT_DIR)

CLIENT_DIR = os.path.join(ROOT_DIR, 'Client')
sys.path.insert(1, CLIENT_DIR)

from utils.messages.voter_messages import Voter_Signin_Message, Voter_Registration_Message, Voter_Ballot_Message
from client.client import Client
from utils.logger_utils import get_logger

logger = get_logger('voter2')

voter2 = Client(b'\x02' * 4, logger)
voter2.start_channel_with_admin(port=3003)

# send sign in request to admin
logger.info(f'Sending sign in request to admin')
signin_message = Voter_Signin_Message('user2', 'bbbb')
voter2.send_message(signin_message.to_bytes(), voter2.admin_sock)

# send registration request to admin
logger.info(f'Sending registration request to admin')
voter_reigstration_message = Voter_Registration_Message(voter2.id)
voter2.send_message(voter_reigstration_message.to_bytes(), voter2.admin_sock)

voter2.receive_message_from_admin()


voter2.connect_with_collector2()
voter2.receive_message_from_collector(voter2.c2_sock)
voter2.close_connection(voter2.c2_sock)

voter2.connect_with_collector1()
voter2.receive_message_from_collector(voter2.c1_sock)
voter2.close_connection(voter2.c1_sock)

voter2.start_channel_with_admin(port=3003)
ballot_message = Voter_Ballot_Message(voter2.all_ballots, voter2.all_shares)
voter2.send_message(ballot_message.to_bytes(), voter2.admin_sock)
voter2.close_connection(voter2.admin_sock)
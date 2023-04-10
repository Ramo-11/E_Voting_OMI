import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT_DIR)

CLIENT_DIR = os.path.join(ROOT_DIR, 'Client')
sys.path.insert(1, CLIENT_DIR)

from utils.messages.voter_messages import Voter_Signin_Message, Voter_Registration_Message
from utils.Message_Type import MESSAGE
from client.client import Client

voter3 = Client(b'\x03' * 4)
voter3.start(port=3003)

# sign in
signin_message = Voter_Signin_Message('user3', 'cccc')
voter3.send_message(signin_message.to_bytes())

# send registration request to admin
voter_reigstration_message = Voter_Registration_Message(voter3.id)
voter3.send_message(voter_reigstration_message.to_bytes())

voter3.receive_message()

# if __name__ == '__main__':
#     voter3 = Client(location=2)
#     shares = []
#     shares_prime = []

#     votes = voter3.start_voting()
#     votes = voter3.generate_voting_vector(votes)

#     # Connect to collector 1
#     voter3.start(port=3001)
#     all_shares = voter3.get_shares()
#     voter3.close_connection()

#     shares.append(all_shares[0])
#     shares_prime.append(all_shares[1])

#     # Connect to collector 2
#     voter3.start(port=3002)
#     all_shares += voter3.get_shares()
#     voter3.close_connection()

#     shares.append(all_shares[0])
#     shares_prime.append(all_shares[1])

#     all_shares = [shares, shares_prime]

#     for vote in votes:
#         ballot = voter3.generate_all_ballots(vote, all_shares)
#         print(f'ballot: {ballot}')

#     voter3.start(port=3003)
#     voter3.send_message(ballot)
#     voter3.close_connection()
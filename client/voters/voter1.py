import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT_DIR)

CLIENT_DIR = os.path.join(ROOT_DIR, 'Client')
sys.path.insert(1, CLIENT_DIR)

from utils.messages.voter_messages import Voter_Signin_Message, Voter_Registration_Message
from utils.Message_Type import MESSAGE
from client.client import Client

voter1 = Client(b'\x01' * 4)
voter1.start(port=3003)

# sign in
signin_message = Voter_Signin_Message('user1', 'aaaa')
voter1.send_message(signin_message.to_bytes())

# send registration request to admin
voter_reigstration_message = Voter_Registration_Message(voter1.id)
voter1.send_message(voter_reigstration_message.to_bytes())

voter1.receive_message()

# if __name__ == '__main__':
#     voter1 = Client(location=1)
#     shares = []
#     shares_prime = []

#     votes = voter1.start_voting()
#     votes = voter1.generate_voting_vector(votes)

#     # Connect to collector 1
#     voter1.start(port=3001)
#     all_shares = voter1.get_shares()
#     voter1.close_connection()

#     shares.append(all_shares[0])
#     shares_prime.append(all_shares[1])

#     # Connect to collector 2
#     voter1.start(port=3002)
#     all_shares += voter1.get_shares()
#     voter1.close_connection()

#     shares.append(all_shares[0])
#     shares_prime.append(all_shares[1])

#     all_shares = [shares, shares_prime]

#     for vote in votes:
#         ballot = voter1.generate_all_ballots(vote, all_shares)
#         print(f'ballot: {ballot}')
    
#     voter1.start(port=3003)
#     voter1.send_message(ballot)
#     voter1.close_connection()
import sys
import time

sys.path.insert(1, '/Users/omar.abdelalim/codespace/E_Voting_OMI')
from client.client_tcp import Client

if __name__ == '__main__':
    voter1 = Client(location=1)

    vote = voter1.start_voting()
    vote = voter1.generate_voting_vector(vote)
    print(f'vooooote is: {vote}')
    # voter1.start(port=3001)
    # voter1.send_message(vote)
    # voter1.close_connection()
    # voter1.start(port=3002)
    # voter1.send_message(vote)
    # voter1.send_message("CSCI 24000,Homework 2, Dr. Xzou")
    # voter1.close_connection()
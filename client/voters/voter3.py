import sys
import time

sys.path.insert(1, '/Users/omar.abdelalim/codespace/E_Voting_OMI')
from client.client_tcp import Client

if __name__ == '__main__':
    voter3 = Client(location=2)
    shares = []
    shares_prime = []

    votes = voter3.start_voting()
    votes = voter3.generate_voting_vector(votes)

    # Connect to collector 1
    voter3.start(port=3001)
    all_shares = voter3.get_shares()
    voter3.close_connection()

    shares.append(all_shares[0])
    shares_prime.append(all_shares[1])

    # Connect to collector 2
    voter3.start(port=3002)
    all_shares += voter3.get_shares()
    voter3.close_connection()

    shares.append(all_shares[0])
    shares_prime.append(all_shares[1])

    all_shares = [shares, shares_prime]

    for vote in votes:
        ballot = voter3.generate_all_ballots(vote, all_shares)
        print(f'ballot: {ballot}')

    voter3.start(port=3003)
    voter3.send_message(ballot)
    voter3.close_connection()
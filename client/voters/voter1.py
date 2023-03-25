import sys
import time

sys.path.insert(1, '/Users/omar.abdelalim/codespace/E_Voting_OMI')
from client.client_tcp import Client

if __name__ == '__main__':
    voter1 = Client(location=1)
    shares = []
    shares_prime = []

    votes = voter1.start_voting()
    votes = voter1.generate_voting_vector(votes)

    # Connect to collector 1
    voter1.start(port=3001)
    all_shares = voter1.get_shares()
    voter1.close_connection()

    shares.append(all_shares[0])
    shares_prime.append(all_shares[1])

    # Connect to collector 2
    voter1.start(port=3002)
    all_shares += voter1.get_shares()
    voter1.close_connection()

    shares.append(all_shares[0])
    shares_prime.append(all_shares[1])

    all_shares = [shares, shares_prime]

    for vote in votes:
        ballot = voter1.generate_all_ballots(vote, all_shares)
        print(f'ballot: {ballot}')
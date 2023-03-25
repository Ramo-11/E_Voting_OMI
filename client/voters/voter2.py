import sys
import time

sys.path.insert(1, '/Users/omar.abdelalim/codespace/E_Voting_OMI')
from client.client_tcp import Client

if __name__ == '__main__':
    voter2 = Client(location=0)
    shares = []
    shares_prime = []

    votes = voter2.start_voting()
    votes = voter2.generate_voting_vector(votes)

    # Connect to collector 1
    voter2.start(port=3001)
    all_shares = voter2.get_shares()
    voter2.close_connection()

    shares.append(all_shares[0])
    shares_prime.append(all_shares[1])

    # Connect to collector 2
    voter2.start(port=3002)
    all_shares += voter2.get_shares()
    voter2.close_connection()

    shares.append(all_shares[0])
    shares_prime.append(all_shares[1])

    all_shares = [shares, shares_prime]

    for vote in votes:
        ballot = voter2.generate_all_ballots(vote, all_shares)
        print(f'ballot: {ballot}')
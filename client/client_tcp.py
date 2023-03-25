import socket

class Client:
    def __init__(self, location):
        self.voting_vector = {
            "What is the best CS class?": ["240", "555", "511"],
            "What is the hardest homework in CSCI 55500?": ["H1", "H2", "H3"],
            "Who is the best professor in the CS department?": ["Xzou", "Kelly", "Andy"]
        } 
        self.server = socket.gethostbyname('localhost')
        self.header = 64
        self.format = 'utf-8'
        self.location = location
    
    def start(self, port=3002):
        """
        Connect to the server through TCP
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.server, int(port)))

    def send_message(self, message):
        """
        Send the length of the message first,
        Then, send the actual message
        """
        encoded_message = str(message).encode(self.format)
        message_length = str(len(encoded_message)).encode(self.format)
        message_length += b' ' * (self.header - len(message_length))
        self.sock.send(message_length)
        self.sock.send(encoded_message)
    
    def get_shares(self):
        share = 0
        share_prime = 0
        self.send_message('give me shares')
        message_from_server = self.sock.recv(self.header).decode(self.format)
        share = int(message_from_server.split(',')[0])
        share_prime = int(message_from_server.split(',')[1])
        return [share, share_prime]

    def close_connection(self):
        """
        Send a closing message to the server,
        Wait for a response from the server to acknowledge the closing,
        And then close the socket connection
        """
        closing_message = 'closing connection'
        self.send_message(closing_message)
        self.sock.close()
        print('Connection closed.')

    def start_voting(self):
        print(list(self.voting_vector.keys())[0])
        print(list(self.voting_vector.values())[0])
        q1_answer = input("")
        if q1_answer not in list(self.voting_vector.values())[0]:
            raise Exception("Answer is not in the list")
        print(list(self.voting_vector.keys())[1])
        print(list(self.voting_vector.values())[1])
        q2_answer = input("")
        if q2_answer not in list(self.voting_vector.values())[1]:
            raise Exception("Answer is not in the list")
        print(list(self.voting_vector.keys())[2])
        print(list(self.voting_vector.values())[2])
        q3_answer = input("")
        if q3_answer not in list(self.voting_vector.values())[2]:
            raise Exception("Answer is not in the list")
        return q1_answer + "," + q2_answer + "," + q3_answer
    
    def generate_voting_vector(self, vote):
        vector = '000000000'
        voting_list = []
        for i in range(len(list(self.voting_vector.keys()))):
            q_vote = vote.split(',')[i]
            q = list(self.voting_vector.values())[i]
            answer_index = q.index(q_vote) + (3 * self.location)
            vector_list = list(vector)
            vector_list[answer_index] = '1'
            new_vector = ''.join(vector_list)
            v = int(new_vector, 2)
            v_prime = int(new_vector[::-1], 2)
            voting_list.append([v, v_prime]) 
        return voting_list
    
    def generate_all_ballots(self, vote, shares):
        ballots = self.generate_ballots(vote[0], shares[0])
        ballots_prime = self.generate_ballots(vote[1], shares[1])
        return [ballots, ballots_prime]

    def generate_ballots(self, vote, shares):
        return vote + sum(shares)
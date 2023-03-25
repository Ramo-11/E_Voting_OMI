import sys

sys.path.insert(1, '/Users/omar.abdelalim/codespace/E_Voting_OMI')
from client.client_tcp import Client

if __name__ == '__main__':
    voter3 = Client()
    connected = True
    while connected:
        message = input('Input (port number first): ')
        if message == 'q':
            connected = False
            message = 'disconnect'
        port = message.split(',')[0]
        message = message.split(',')[1]
        voter3.start(port=port)
        voter3.send_message(message)
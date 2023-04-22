import os
import sys

from admin_server import Admin_Server

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)

from utils import Message_Type
from utils.messages.admin_message import Registration_Message, Metadata_Message, Voters_Information

if __name__ == '__main__':
    print(f'Welcome to OMI E-Voting System\n\n')
    admin = Admin_Server("Admin", port=3003)

    print(f'Starting the initialization process')
    # Connect to collector 1 and send the message
    admin.connect(port=3001)
    admin_message = Registration_Message(b'\x00')
    admin_message = admin_message.to_bytes()
    print(f'\nSending collector 1 registration message')
    admin.send_message(admin_message)
    message_received = admin.receive_message()
    accept = message_received[-1:]
    if accept == b'\x01':
        print('Collector 1 accepted')
    admin.close_connection()

    # Connect to collector 2 and send the message
    admin.connect(port=3002)
    message = Registration_Message(b'\x01')
    message = message.to_bytes()
    print(f'\nSending collector 2 registration message')
    admin.send_message(message)
    message_received = admin.receive_message()
    accept = message_received[-1:]
    if accept == b'\x01':
        print('All collectors accepted')

    # Send collector 2 the information of collector 1 so they can connect
    message = Metadata_Message(3001)
    message = message.to_bytes()
    admin.send_message(message)
    admin.close_connection()


    print(f'\n\nStarting the Voters Registration process\n')
    # Admin now acts as a server and listens to connections from voters
    # Admin should also be getting the ids of each user here



    # voters send their ids to admin, and immediately after that, voters connect to collectors
    admin.start()



    # admin sends voters ids to collectors
    # admin.connect(port=3001)
    # admin_message = Voters_Information(admin.voter_ids[0], admin.voter_ids[1], admin.voter_ids[2])
    # admin_message = admin_message.to_bytes()
    # admin.send_message(admin_message)
    # admin.close_connection()

    # admin.connect(port=3002)
    # admin_message = Voters_Information(admin.voter_ids[0], admin.voter_ids[1], admin.voter_ids[2])
    # admin_message = admin_message.to_bytes()
    # admin.send_message(admin_message)
    # admin.close_connection()
import os
import sys

from admin_server import Admin_Server

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)

from utils import Message_Type
from utils.messages.admin_message import Registration_Message, Metadata_Message, Voters_Information

if __name__ == '__main__':
    admin = Admin_Server(port=3003)

    # Connect to collector 1 and send the message
    admin.connect(port=3001)
    admin_message = Registration_Message(b'\x00')
    admin_message = admin_message.to_bytes()
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
    admin.send_message(message)
    message_received = admin.receive_message()
    accept = message_received[-1:]
    if accept == b'\x01':
        print('All collectors accepted')
    message = Metadata_Message(3001)
    message = message.to_bytes()
    admin.send_message(message)
    admin.close_connection()

    # Admin now acts as a server and listens to connections from voters
    admin.start()

    
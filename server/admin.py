import os
import sys

from admin_server import Admin_Server

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)

from utils import Message_Type
from utils.messages.admin_message import Admin_Message

if __name__ == '__main__':
    admin = Admin_Server(port=3003)

    # Connect to collector 1 and send the message
    admin.connect(port=3001)
    admin_message = Admin_Message(Message_Type.MESSAGE.COLLECT_REQUEST, 1)
    admin_message = admin_message.to_bytes()
    admin.send_message(admin_message)
    message_received = admin.receive_message()
    admin.close_connection()

    # Connect to collector 2 and send the message
    admin.connect(port=3002)
    admin_message = Admin_Message(Message_Type.MESSAGE.COLLECT_REQUEST, 1)
    admin_message = admin_message.to_bytes()
    admin.send_message(admin_message)
    message_received = admin.receive_message()
    admin.close_connection()
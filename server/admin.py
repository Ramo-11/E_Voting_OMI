import os
import sys

from admin_server import Admin_Server

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)

from utils.messages.admin_message import Registration_Message, Metadata_Message
from utils.logger_utils import get_logger

logger = get_logger('admin')

if __name__ == '__main__':
    logger.info(f'Welcome to OMI E-Voting System')
    admin = Admin_Server("Admin", logger, port=3003)

    logger.info(f'******** Starting the initialization process ********')

    # Connect to collector 1 and send the message
    admin.connect(port=3001)
    registration_message = Registration_Message(b'\x00', admin.pk, admin.pk_length)
    registration_message = registration_message.to_bytes()
    logger.info(f'Sending collector 1 registration message')
    admin.send_message(registration_message)
    message_received = admin.receive_message()
    accept = message_received[-1:]
    if accept == b'\x01':
        logger.info('Collector 1 accepted')
    admin.close_connection()

    # Connect to collector 2 and send the message
    admin.connect(port=3002)
    registration_message = Registration_Message(b'\x01', admin.pk, admin.pk_length)
    registration_message = registration_message.to_bytes()
    logger.info(f'Sending collector 2 registration message')
    admin.send_message(registration_message)
    message_received = admin.receive_message()
    accept = message_received[-1:]
    if accept == b'\x01':
        logger.info('All collectors accepted their registration request')

    # Send collector 2 the information of collector 1 so they can connect
    message = Metadata_Message(3001)
    message = message.to_bytes()
    admin.send_message(message)
    admin.close_connection()


    logger.info(f'******** Starting the Voters Registration process ********')
    
    # Admin now acts as a server and listens to connections from voters
    # Admin should also be getting the ids of each user here
    # voters send their ids to admin, and immediately after that, voters connect to collectors
    admin.start()
from client_tcp import Client

import sys
sys.path.insert(1, r'C:\Users\ismae\E_Voting_OMI')
from  utils.messages import admin_message


message_type = 'TYPE_COLLECT_REQUEST'
election_id = '1234567890123456'
collector1_index = 1
collector2_index = 2
pk_length = 15
pk = 'my public key'
collector_key_hash = 'my collector key hash'

collecter1_message = admin_message.Admin_Message(message_type, election_id, collector1_index, pk_length, pk, collector_key_hash)
collecter1_message = collecter1_message.to_bytes()

collecter2_message = admin_message.Admin_Message(message_type, election_id, collector2_index, pk_length, pk, collector_key_hash)
collecter2_message = collecter2_message.to_bytes()

if __name__ == '__main__':
    admin = Client()
    admin.start(port=3001)
    admin.send_message(collecter1_message)
    
    admin.start(port=3002)
    admin.send_message(collecter2_message)
   
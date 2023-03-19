from client_tcp import Client
from ..utils.messages.admin_message import Admin_Message

message_type = 'TYPE_COLLECT_REQUEST'
election_id = '1234567890123456'
collector_index = 0
pk_length = 15
pk = 'my public key'
collector_key_hash = 'my collector key hash'

message = Admin_Message(message_type, election_id, collector_index, pk_length, pk, collector_key_hash)
message = message.to_bytes()

if __name__ == '__main__':
    admin = Client()
    # connected = True
    admin.start(port=3001)
    admin.send_message(message)
    admin.start(port=3002)
    admin.send_message(message)
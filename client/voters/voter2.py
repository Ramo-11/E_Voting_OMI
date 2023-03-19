from client_tcp import Client

if __name__ == '__main__':
    voter2 = Client()
    connected = True
    while connected:
        message = input('Input (port number first): ')
        if message == 'q':
            connected = False
            message = 'disconnect'
        port = message.split(',')[0]
        message = message.split(',')[1]
        voter2.start(port=port)
        voter2.send_message(message)
from server_tcp import Server

if __name__ == '__main__':
    collector1 = Server(port=3001)
    collector1.start()
from server_tcp import Server

if __name__ == '__main__':
    collector2 = Server(port=3002)
    collector2.start()
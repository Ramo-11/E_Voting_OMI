from server_tcp import Server

if __name__ == '__main__':
    Admin = Server(port=3003)
    Admin.start()
import socket
import threading

class Server:
    def __init__(self, port=3000):
        self.port = port
        self.server = socket.gethostbyname(socket.gethostname())
        self.header = 64
        self.format = 'utf-8'
        
    def start(self):
        print("Starting Server")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.server, self.port))
        self.sock.listen()
        print(f"Server is listening on {self.server}")
        while True:
            client, address = self.sock.accept()
            print("Connection from: {}".format(str(address)))
            self.thread = threading.Thread(target=self.listen_to_client, args=(client, address))
            self.thread.start()
    
    def listen_to_client(self, client, address):
        connected = True
        while connected:
            message_length = client.recv(64).decode(self.format)
            message = client.recv(message_length).decode(self.format)
            print(f"[{address}]: {message}")
            if message == "disconnect":
                connected = False
        client.close()
        
        
def main():
    server = Server()
    server.start()
    
if __name__ == "__main__":
    main()
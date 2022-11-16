import socket

IP = 'localhost'
PORT = 5555

class Network():
    def __init__(self) -> None:
        self.client = None

    def conn(self) -> None:
        # connect to server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((IP, PORT))
        print(self.client)

    def send(self, data: str) -> str:
        try:
            self.client.send((data).encode())
            reply = self.client.recv(2048).decode()
            return reply
        except socket.error as e:
            return str(e)
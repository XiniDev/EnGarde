import socket

IP = 'localhost'
PORT = 5555

client = None

def conn() -> None:
    # connect to server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP, PORT))

def send(data: str) -> str:
    try:
        client.send((data).encode())
        reply = client.recv(2048).decode()
        return reply
    except socket.error as e:
        return str(e)
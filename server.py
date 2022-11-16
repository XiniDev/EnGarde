import socket, threading, time

IP = 'localhost'
PORT = 5555

# bind server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((IP, PORT))

# shows how many players are in the server
total_players = 0

# variables for storing player 1 and 2
players = {}

def conn_handler(conn, addr):
    # globals
    global total_players, players

    # connected
    print("Client connected on: ", conn)
    
    # connect player 1 and player 2
    total_players += 1
    print(f"Player {total_players} has connected")
    players[conn] = total_players

    time.sleep(1)

    # connection loop
    while True:
        try:
            data = conn.recv(2048)
            reply = data.decode('utf-8')
            if not data:
                print(f"Player {players[conn]} with address: {addr} has disconnected")
                conn.send(str.encode("You have disconnected"))
                print("broke because not data")
                break
            else:
                print(f"Recieved: {reply}")
                print(f"Sending: {reply}")
            if len(players) < 2:
                conn.sendall(str.encode(reply))
            else:
                for key in players:
                    if conn != key:
                        key.sendall(str.encode(reply))
        except:
            print("broke on exception")
            break

    popped = players.pop(conn)
    if popped < total_players:
        for k, v in players.items():
            if v > popped:
                v -= 1
    total_players -= 1

    # end connection
    print("Client disconnected on: ", conn)
    conn.close()

# server initialisation
def init_server():
    print("Done!")
    run()

# run server
def run():
    server.listen()
    while True:
        conn, addr = server.accept()
        print("Connected to: ", addr)

        thread = threading.Thread(target = conn_handler, args = (conn, addr))
        thread.start()

# main function
def main():
    print("Initialising server...")
    init_server()

if __name__ == '__main__':
    main()
import socket, threading, time

IP = 'localhost'
PORT = 5555

# bind server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((IP, PORT))

# determines if it is player 1 turn to connect
is_p1 = True

# variables for storing player 1 and 2
player_1 = None
player_2 = None

def conn_handler(conn, addr):
    # globals
    global is_p1, player_1, player_2

    # connected
    print("Client connected on: ", conn)
    
    # connect player 1 and player 2
    global player_1, player_2

    if is_p1 == True:
        is_p1 = False
        print("Player 1 has connected")
        player_1 = conn
    else:
        print("Player 2 has connected")
        player_2 = conn

    time.sleep(1)

    # connection loop
    while True:
        try:
            data = conn.recv(2048)
            reply = data.decode('utf-8')
            if not data:
                print(f"{addr} has disconnected")
                conn.send(str.encode("You have disconnected"))
                break
            else:
                print("Recieved: " + reply)
                print("Sending: " + reply)
            conn.sendall(str.encode(reply))
            # if is_p1:
            #     player_1.send(bytes(data))
            # else:
            #     player_2.send(bytes(data))
        except:
            break
    
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
import socket
import threading
import random

# Global storage for slave connections
slaves = []

def handle_slave(conn):
    """Handles incoming messages from slaves."""
    while True:
        try:
            # Keep the connection open to receive future updates if needed
            data = conn.recv(1024)
            # No actual implementation of data handling from slave in this example
        except:
            break

def handle_client(conn):
    """Handles incoming messages from clients."""
    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break
            
            command, key, value = data.split(" ")
            print(command, key, value)
            if command == "WRITE":
                # Randomly select a slave to write
                selected_slave = random.choice(slaves)
                # print(selected_slave)
                selected_slave.sendall(data.encode())
            elif command == "READ":
                # Assume we have a mechanism to wait for slave responses.
                # This code simplifies that logic.
                print(key)
                responses = []
                for slave in slaves:
                    slave.sendall(data.encode())
                    response = slave.recv(1024).decode()
                    print(response)
                    if response:  # If a slave sends back a response, add it to the list
                        responses.append(response)
                
                # If at least one slave responded, send the first valid response back to the client.
                if responses:
                    conn.sendall(responses[0].encode())

        except:
            break

def master_server():
    host = 'localhost'
    port = 12345

    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(5)

    print("Master Server Started.")
    try:
        while True:
            conn, addr = s.accept()
            print(f"Connected by {addr}")

            # Determine if connected entity is a slave or a client based on initial message
            data = conn.recv(1024).decode()
            if data == "SLAVE":
                slaves.append(conn)
                threading.Thread(target=handle_slave, args=(conn,)).start()
            else:
                threading.Thread(target=handle_client, args=(conn,)).start()
    except KeyboardInterrupt:
        print("Shutting down server.")
    finally:
        s.close()

if __name__ == '__main__':
    master_server()

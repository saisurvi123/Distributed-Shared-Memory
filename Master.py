# import socket
# import threading
# import random

# # Global storage for slave connections and key mapping to slaves
# slaves = []
# key_to_slaves = {}  # Dictionary to store which slaves have which keys

# def handle_slave(conn):
#     """Handles incoming messages from slaves."""
#     while True:
#         try:
#             data = conn.recv(1024)
#             # No actual implementation of data handling from slave in this example
#         except:
#             break

# def handle_client(conn):
#     """Handles incoming messages from clients."""
#     while True:
#         try:
#             data = conn.recv(1024).decode()
#             if not data:
#                 break
            
#             command, key, value = data.split(" ")
#             print(command, key, value)
#             if command == "WRITE":
#                 # Randomly select 2 slaves to write and remember which slaves have the key
#                 selected_slaves = random.sample(slaves, 2)
#                 key_to_slaves[key] = selected_slaves
#                 for slave in selected_slaves:
#                     slave.sendall(data.encode())

#             elif command == "READ":
#                 # Check if the key is mapped to specific slaves
#                 if key in key_to_slaves:
#                     selected_slaves = key_to_slaves[key]
#                     responses = []
#                     for slave in selected_slaves:
#                         print(f"Sending read request to slave: {slave}")
#                         slave.sendall(data.encode())
#                         response = slave.recv(1024).decode()
#                         if response:  # If a slave sends back a response, add it to the list
#                             responses.append(response)
#                             break

#                     if responses:
#                         print(f"Sending response to client: {responses[0]}")
#                         conn.sendall(responses[0].encode())
#                     else:
#                         print("No valid responses received from selected slaves.")
#                         conn.sendall(b"No valid responses received from selected slaves.")
#                 else:
#                     print(f"Key {key} not found in any slave.")
#                     conn.sendall(b"Key not found in any slave.")
#         except:
#             break

# def master_server():
#     host = 'localhost'
#     port = 12345

#     s = socket.socket()
#     s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     s.bind((host, port))
#     s.listen(5)

#     print("Master Server Started.")
#     try:
#         while True:
#             conn, addr = s.accept()
#             print(f"Connected by {addr}")

#             data = conn.recv(1024).decode()
#             if data == "SLAVE":
#                 slaves.append(conn)
#                 threading.Thread(target=handle_slave, args=(conn,)).start()
#             else:
#                 threading.Thread(target=handle_client, args=(conn,)).start()
#     except KeyboardInterrupt:
#         print("Shutting down server.")
#     finally:
#         s.close()

# if __name__ == '__main__':
#     master_server()


import socket
import threading
import random
import time

# Global storage for slave connections and key mapping to slaves
slaves = []
key_to_slaves = {}  # Dictionary to store which slaves have which keys
lock = threading.Lock()  # Lock for data store access

def handle_slave(conn):
    """Handles incoming messages from slaves."""
    while True:
        try:
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
                # Randomly select 2 slaves to write and remember which slaves have the key
                selected_slaves = random.sample(slaves, 2)
                with lock:
                    key_to_slaves[key] = selected_slaves
                for slave in selected_slaves:
                    slave.sendall(data.encode())

            elif command == "READ":
                # Check if the key is mapped to specific slaves
                if key in key_to_slaves:
                    selected_slaves = key_to_slaves[key]
                    responses = []
                    for slave in selected_slaves:
                        print(f"Sending read request to slave: {slave}")
                        slave.sendall(data.encode())
                        response = slave.recv(1024).decode()
                        if response:  # If a slave sends back a response, add it to the list
                            responses.append(response)

                    if responses:
                        print(f"Sending response to client: {responses[0]}")
                        conn.sendall(responses[0].encode())
                    else:
                        print("No valid responses received from selected slaves.")
                        conn.sendall(b"No valid responses received from selected slaves.")
                else:
                    print(f"Key {key} not found in any slave.")
                    conn.sendall(b"Key not found in any slave.")
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

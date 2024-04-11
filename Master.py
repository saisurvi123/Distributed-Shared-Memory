import socket
import threading
import random
import select
import time

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


def send_request_to_slave(slave_socket, request_data, received_responses, timeout=10, retry_interval=2):
    """
    Send a request to a slave continuously until a valid response is received,
    with a timeout for each attempt and a pause between retries.
    A valid response is considered as "key value" where value is not "NOT_FOUND".
    """
    slave_socket.settimeout(timeout)
    
    while not received_responses["received"]:
        try:
            print(f"Sending request to slave: {request_data}")
            slave_socket.sendall(request_data.encode())
            
            response = slave_socket.recv(1024).decode()
            # Parse the response to check if it's valid (not "NOT_FOUND")
            if response:
                parts = response.split(" ", 1)  # Split response into key and value
                if len(parts) == 2 and parts[1].strip() != "NOT_FOUND" and not received_responses["received"]:
                    print(f"Received valid response from a slave: {response}")
                    received_responses["response"] = response
                    received_responses["received"] = True
                    return  # Exit the thread once a valid response is received
                else:
                    print(f"Invalid or not found response received: {response}")
        except socket.timeout:
            print("Timeout. Retrying...")
            time.sleep(retry_interval)  # Wait a bit before retrying
        except Exception as e:
            print(f"An error occurred: {e}")
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
                # selected_slave = random.choice(slaves)
                # # print(selected_slave)
                # selected_slave.sendall(data.encode())
                for slave in slaves:
                    slave.sendall(data.encode())

            elif command == "READ":    
                received_responses = {"received": False, "response": None}
                threads = []

                for slave in slaves:
                    thread = threading.Thread(target=send_request_to_slave, args=(slave, data, received_responses))
                    threads.append(thread)
                    thread.start()
                
                for thread in threads:
                    thread.join()

                if received_responses["received"]:
                    print(f"Final response: {received_responses['response']}")
                    conn.sendall(received_responses["response"].encode())
                else:
                    print("No responses received from any slaves.")
                    conn.sendall("NOT_FOUND".encode())

                
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

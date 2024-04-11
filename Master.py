import socket
import threading
import random
import select
import time

# Global storage for slave connections
slaves = []
key_to_slaves = {}  # Dictionary to store which slaves have which keys


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
            
            if response:
                print(f"Received valid response from a slave: {response}")
                received_responses["response"] = response
                received_responses["received"] = True
                return  # Exit the thread once a valid response is received
                
        except socket.timeout:
            print("Timeout. Retrying...")
            time.sleep(retry_interval)  # Wait a bit before retrying
        except Exception as e:
            print(f"An error occurred: {e}")
            break

def rec_ack_from_slave(slave_socket, request_data, received_responses, timeout=10, retry_interval=2):
    """
    Receive acknowledgment from a slave continuously until a valid response is received,
    with a timeout for each attempt and a pause between retries.
    A valid response is considered as "ACK".
    """
    slave_socket.settimeout(timeout)
    
    while not received_responses[slave_socket]:
        try:
            print(f"Waiting for acknowledgment from slave: {request_data}")
            slave_socket.sendall(request_data.encode())
            response = slave_socket.recv(1024).decode()
            
            if response:
                print(f"Acknowledgment received from a slave: {response}")
                received_responses[slave_socket] = True
                return  # Exit the thread once a valid response is received
                
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
                selected_slaves = random.sample(slaves, 2)  # Randomly select 2 slaves
                key_to_slaves[key] = selected_slaves  # Store selected slaves for this key
                # for slave in selected_slaves:
                #     slave.sendall(data.encode())
                received_responses = {slave: False for slave in selected_slaves}

                threads = []
                for slave in selected_slaves:
                    thread = threading.Thread(target=rec_ack_from_slave, args=(slave, data, received_responses))
                    threads.append(thread)
                    thread.start()

                for thread in threads:
                    thread.join()

                not_received_slaves = [slave for slave, ack in received_responses.items() if not ack]
                if not_received_slaves:
                    print("No acknowledgment received from some slaves. Removing them.")
                    for slave in not_received_slaves:
                        slaves.remove(slave)
                        for key, value in key_to_slaves.items():
                            if slave in value:
                                key_to_slaves[key].remove(slave)
                    conn.sendall("WRITE_DONE".encode())
                else:
                    print("Write operation successful.")
                    conn.sendall("WRITE_DONE".encode())
            elif command == "READ":    
                if key not in key_to_slaves:
                    print(f"Key {key} not found in any slave.")
                    conn.sendall("NOT_FOUND".encode())
                else :
                    received_responses = {"received": False, "response": None}
                    selected_slaves = key_to_slaves[key]
                    threads = []

                    for slave in selected_slaves:
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
def check_port_in_use(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("localhost", port))
    except socket.error as e:
        if e.errno == socket.errno.EADDRINUSE:
            print(f"Port {port} is already in use")
        else:
            # Handle other socket errors if needed
            print(f"Error binding to port {port}: {e}")
        return True
    finally:
        s.close()
    return False

def master_server():
    host = 'localhost'
    # port = random.randint(1024, 49151) 
    port = 12345
    if(check_port_in_use(port)):
        port = 12346
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

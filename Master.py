import socket
import threading
import random
import select
import time
from math import ceil
import json
from collections import Counter
from termcolor import colored

# Global storage for slave connections
slaves = []
key_to_slaves = {}  # Dictionary to store which slaves have which keys
backup = False

def connect_to_backup_master():
    global backup_master_conn
    backup_host = 'localhost'  # Adjust as necessary
    backup_port = 12346        # Backup master's listening port
    backup_master_conn = socket.create_connection((backup_host, backup_port))
    print("Connected to backup master.")

def send_update_to_backup(key, slaves):
    """Send updates to the backup master for a specific key and its corresponding slave list."""
    if backup_master_conn:
        try:
            # Prepare a serializable list of slave identifiers (IP addresses and ports)
            slave_identifiers = [slave.getpeername() for slave in slaves]
            update_data = pickle.dumps((key, slave_identifiers))
            backup_master_conn.sendall(update_data)
            print(f"Sent update for key {key} to backup master.")
        except Exception as e:
            print(f"Failed to send update to backup master: {e}")

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
            # print(f"Sending request to slave: {request_data}")
            print(colored(f"Sending request to slave: {request_data}", 'cyan'))
            slave_socket.sendall(request_data.encode())
            
            response = slave_socket.recv(1024).decode()
            
            if response:
                print(colored(f"Received valid response from a slave: {response}", 'green'))
                received_responses["response"] = response
                received_responses["received"] = True
                return  # Exit the thread once a valid response is received
                
        except socket.timeout:
            print("Timeout. Retrying...")
            time.sleep(retry_interval)  # Wait a bit before retrying
        except Exception as e:
            print(f"An error occurred: {e}")
            break
def send_requests_to_all_slaves(slave_socket, request_data, received_responses, timeout=10, retry_interval=2):
    slave_socket.settimeout(timeout)
    
    while not received_responses[slave_socket]:
        try:
            # print(f"Sending request to slave: {request_data}")
            print(colored(f"Sending request to slave: {request_data}", 'cyan'))
            slave_socket.sendall(request_data.encode())
            
            response = slave_socket.recv(1024).decode()
            
            if response:
                # print(f"Received valid response from a slave: {response}")
                print(colored(f"Received valid response from a slave: {response}", 'green'))
                received_responses[slave_socket] = response
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
            print(f"Waiting for acknowledgment from slave")
            slave_socket.sendall(request_data.encode())
            response = slave_socket.recv(1024).decode()
            
            if response:
                # print(f"Acknowledgment received from a slave: {response}")
                print(colored(f"Acknowledgment received from a slave: {response}", 'green'))
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
            # print("Received from Client: ", data)
            print(colored(f"Received from Client: {data}", 'yellow'))
            if not data:
                break
            
            command, key, value = data.split(" ")
            # print(command, key, value)
            if command == "WRITE":
                # print(ceil(len(slaves) * 0.5))def send_message(host, port, message):
                selected_slaves = random.sample(slaves, ceil((len(slaves)+1.0) * 0.5))
                # selected_slaves = random.sample(slaves, 2)
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
                    # print("Write operation successful.")
                    print(colored("Write operation successful.", 'cyan'))
                    conn.sendall("WRITE_DONE".encode())
                # if(backup == False):
                #     try:
                #         port1 = 12345
                #         if(check_port_in_use(12345)):
                #             port1 = 12346
                #         else:
                #             break
                #         host = 'localhost'
                #         # message = f"REMOVESLAVE"
                #         s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                #         s.connect((host, port1))
                #         # message = json.dumps({"slaves": slaves, "key_to_slaves": key_to_slaves})
                #         message = "BACKUP"
                #         s.sendall(message.encode())
                #         s.close()
                #         print(f"Message '{message}' sent to {host}:{port1}")
                #     except Exception as e:
                #         print(f"Error sending message: {e}")
            elif command == "READ":    
                if key not in key_to_slaves:
                    # print(f"Key {key} not found in any slave.")
                    # conn.sendall("NOT_FOUND".encode())
                    # print("Going into the loop")
                    # print(len(slaves))
                    threads = []
                    rec_response = {slave: None for slave in slaves}
                    for slave in slaves:
                        thread = threading.Thread(target=send_requests_to_all_slaves, args=(slave, data, rec_response))
                        threads.append(thread)
                        thread.start()
                    for thread in threads:
                        thread.join()
                    
                    if rec_response:
                        responses = [response for response in rec_response.values() if response != "NOT_FOUND"]
                        cnt = 0
                        if not responses:  # No valid responses
                            conn.sendall("NOT_FOUND".encode())
                        else:
                            response_counts = Counter(responses)
                            majority_response = max(response_counts, key=response_counts.get)
                            associated_slaves = [slave for slave, response in rec_response.items() if response == majority_response]
                            print(f"Majority response: {majority_response}")
                            conn.sendall(majority_response.encode())
                            key, value = majority_response.split(" ")
                            key_to_slaves[key] = associated_slaves      
                    else:
                        print("No responses received from any slaves.")
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
                        key, value = received_responses["response"].split(" ")
                        print(colored(f"Final response: {value}", 'cyan'))
                        conn.sendall(received_responses["response"].encode())
                    else:
                        print("No responses received from any slaves.")
                        print(colored(f"Final response: NOT_FOUND", 'cyan'))
                        conn.sendall("NOT_FOUND".encode())
                
        except:
            break

def handle_backup(conn):
    """Handles incoming messages from clients."""
    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break
            if data == "BACKUP":
                print("Backup server connected.")
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
            if(data == "CLIENT"):
                print(colored("Client connected.", 'yellow'))
            elif data == "SLAVE":
                print(colored("Slave connected.", 'green'))
            if data == "SLAVE":
                slaves.append(conn)
                threading.Thread(target=handle_slave, args=(conn,)).start()
            elif data == "BACKUP":
                backup = True
                print("Backup server connected.")
            else:
                threading.Thread(target=handle_client, args=(conn,)).start()
    except KeyboardInterrupt:
        print("Shutting down server.")
    finally:
        s.close()

if __name__ == '__main__':
    master_server()

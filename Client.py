import socket
import time
from termcolor import colored

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

def connect_to_master(host, port):
    while True:
        try:
            s = socket.socket()
            if(not check_port_in_use(port)):
                port = port+1
                s = connect_to_master(host, port)
                return s
            else:
                s.connect((host, port))
                s.sendall(b"CLIENT")
                return s
        except Exception as e:
            print(f"Error connecting to master server on port {port}: {e}")
            # port = port + 1
            s = connect_to_master(host, port)
            print("Retrying in 5 seconds...")
            time.sleep(5)
            
def client():
    host = 'localhost'
    port = 12345 if check_port_in_use(12345) else 12346
    # port = 12346
    while(True):
        try:
            # s = connect_to_master(host, port)
            s = socket.socket()
            s.connect((host, port))
            print(colored("Connected to master server", 'yellow'))
            s.sendall(b"CLIENT")
            while True:
                # Ask the user for the operation they want to perform
                operation = input("Enter operation (WRITE/READ/EXIT): ").upper()
                # s.sendall("READ 0".encode())
                # response = s.recv(1024).decode()
                if operation == 'EXIT':
                    print("Exiting client.")
                    return
                elif operation in ['WRITE', 'READ']:
                    key = input("Enter key: ")
                    if operation == 'WRITE':
                        value = input("Enter value: ")
                        print(colored(f"Sending WRITE operation for {key} with value {value}", 'yellow'))  # Color the message in yellow
                        s.sendall(f"{operation} {key} {value}".encode())
                        response = s.recv(1024).decode()
                        print(colored(f"Response from server: {response}", 'cyan'))  # Color the response in light blue
                    elif operation == 'READ':
                        print(colored(f"Sending READ operation for {key}", 'yellow'))
                        s.sendall(f"{operation} {key} ".encode())  # Note the space at the end to match split expectation
                        response = s.recv(1024).decode()
                        key, value = response.split()
                        print(colored(f"Response from server: {value}", 'cyan'))  # Color the response in light blue
                else:
                    print("Invalid operation. Please try again.")
                time.sleep(1)
        except socket.timeout:
            print("Timeout. Retrying...")
            retry_interval = 2
            time.sleep(retry_interval) 
        except Exception as e:
            print(f"Error connecting to master server on port {port}: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)
            continue

if __name__ == '__main__':
    client()

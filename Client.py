import socket
import time
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

def client():
    host = 'localhost'
    port = 12345
    # if(check_port_in_use(12345)):
    #     port = 12345
    # else:
    #     port = 12346

    with socket.socket() as s:
        s.connect((host, port))
        s.sendall(b"CLIENT")
        
        while True:
            # Ask the user for the operation they want to perform
            operation = input("Enter operation (WRITE/READ/EXIT): ").upper()
            
            if operation == 'EXIT':
                print("Exiting client.")
                break
            elif operation in ['WRITE', 'READ']:
                key = input("Enter key: ")
                if operation == 'WRITE':
                    value = input("Enter value: ")
                    print(f"Sending WRITE operation for {key} with value {value}")
                    s.sendall(f"{operation} {key} {value}".encode())
                    response = s.recv(1024).decode()
                elif operation == 'READ':
                    print(f"Sending READ operation for {key}")
                    s.sendall(f"{operation} {key} ".encode())  # Note the space at the end to match split expectation
                    response = s.recv(1024).decode()
                    print(f"Response from server: {response}")
            else:
                print("Invalid operation. Please try again.")
                
            # Adding a small delay after each operation for simplicity
            time.sleep(1)

if __name__ == '__main__':
    client()

import socket
import time

def client():
    host = 'localhost'
    port = 12345

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

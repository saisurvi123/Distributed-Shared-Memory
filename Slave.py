import socket
import time

data_store = {}

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
                s.sendall(b"SLAVE")
                return s
        except Exception as e:
            print(f"Error connecting to master server on port {port}: {e}")
            # port = port + 1
            s = connect_to_master(host, port)
            print("Retrying in 5 seconds...")
            time.sleep(50)
def slave_server():
    host = 'localhost'
    port = 12345 if check_port_in_use(12345) else 12346
    master_host = 'localhost'
    connected = False
    while True:
        try:
            s = connect_to_master(master_host, port)

            while True:
                data = s.recv(1024).decode()
                if not data:
                    break

                command, key, value = data.split(" ")
                if command == "WRITE":
                    print(f'writing data {key} {value}')
                    data_store[key] = value
                    response = f"{key} {value} ACK"
                    try:
                        s.sendall(response.encode())
                    except Exception as e:
                        print(f"Error sending ACK: {e}")
                elif command == "READ":
                    print(f'reading key {key}')
                    value = data_store.get(key, "NOT_FOUND")
                    print(value)
                    response = f"{key} {value}"  # Append termination string
                    try:
                        s.sendall(response.encode())
                    except Exception as e:
                        print(f"Error sending response: {e}")

            s.close()  # Close connection before retrying
        except KeyboardInterrupt:
            print("Keyboard interrupt received, shutting down.")
            break
        except Exception as ex:
            print(f"Error in slave server loop: {ex}")
            print("Retrying connection...")
            time.sleep(50)

if __name__ == '__main__':
    slave_server()

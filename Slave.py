import socket

data_store = {}

def slave_server():
    host = 'localhost'
    port = 12345
    master_host = 'localhost'

    with socket.socket() as s:
        s.connect((master_host, port))
        s.sendall(b"SLAVE")
        
        while True:
            data = s.recv(1024).decode()
            if not data:
                break
            
            command, key, value = data.split(" ")
            if command == "WRITE":
                print(f'writing data {key} {value}')
                data_store[key] = value
            elif command == "READ":
                print(f'reading key {key}')
                value = data_store.get(key, None)
                if value is not None:
                    s.sendall(f"{key} {value}".encode())
                else:
                    s.sendall("NOT_FOUND".encode())  # Optionally handle not found case


if __name__ == '__main__':
    slave_server()

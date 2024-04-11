import socket
import signal

data_store = {}

def handle_keyboard_interrupt(conn):
    """Handle keyboard interrupt by sending REMOVESLAVE command to the master."""
    print("Keyboard interrupt detected. Sending REMOVESLAVE command to master.")
    try:
        conn.sendall(b"REMOVESLAVE")
    except Exception as e:
        print(f"Error sending REMOVESLAVE command: {e}")

def slave_server(conn):
    # signal.signal(signal.SIGINT, handle_keyboard_interrupt(conn=conn))
    try:
        conn.sendall(b"SLAVE")
            
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
                
            command, key, value = data.split(" ")
            if command == "WRITE":
                print(f'writing data {key} {value}')
                data_store[key] = value
            elif command == "READ":
                print(f'reading key {key}')
                value = data_store.get(key, "NOT_FOUND")
                print(value)
                response = f"{key} {value}"  # Append termination string
                try:
                    conn.sendall(response.encode())
                except Exception as e:
                    print(f"Error sending response: {e}")
    except KeyboardInterrupt:
        handle_keyboard_interrupt(conn)
        pass  # Ignore keyboard interrupt during normal operation

if __name__ == '__main__':
    host = 'localhost'
    port = 12345

    # Set up signal handler for keyboard interrupt
    # signal.signal(signal.SIGINT, handle_keyboard_interrupt(conn=conn))

    try:
        with socket.socket() as s:
            s.connect((host, port))
            slave_server(s)
    except ConnectionRefusedError:
        print("Error connecting to the master server.")

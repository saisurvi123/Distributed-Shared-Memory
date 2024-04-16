import socket
import pickle
import threading

HOST = 'localhost'
BACKUP_PORT = 12346
key_to_slaves = {}  # Dictionary to maintain the current state of key to slave mappings

def handle_updates(conn):
    """Handle incoming updates from the primary master."""
    try:
        while True:
            data = conn.recv(1024)
            print(data)
            if not data:
                break  # Break the loop if connection is lost
            key, value = pickle.loads(data)  # Unpickle the received data
            key_to_slaves[key] = value  # Update the local dictionary
            print(f"Received update from Primary: {key} -> {value}")
    except Exception as e:
        print(f"Error receiving updates: {e}")
    finally:
        print("Lost connection to primary master, preparing to take over.")
        # take_over_as_primary()  # Attempt to take over as the primary master

def start_backup_master():
    """Run the backup master server, listening for updates from the primary master."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, BACKUP_PORT))
    server_socket.listen(1)
    print("Backup Master is ready and listening for state updates...")
    while True:
        conn, addr = server_socket.accept()
        print(f"Connected to Primary Master at {addr}")
        handle_updates(conn)

def take_over_as_primary():
    """Function to promote this server to primary master."""
    # Implement logic to promote this server to primary master
    print("This server is now acting as the primary master.")
    # Potentially start listening on the primary port or perform other necessary state changes

if __name__ == '__main__':
    start_backup_master()

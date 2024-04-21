# Distributed Shared Memory System

## Overview
This Distributed Shared Memory (DSM) system demonstrates READ and WRITE operations between multiple clients and slaves, coordinated by a master server, using Python and socket programming on a single machine. The system emphasizes fault tolerance through ACK bits and data consistency by distributing WRITE operations to a subset of slaves.

## Features
- *Multiple Clients and Slaves:* Supports simultaneous connections of multiple clients and slaves.
- *Fault Tolerance:* Uses ACK bits from slaves to the master to confirm successful operations.
- *Consistency and Efficiency:* Distributes WRITE operations across a subset of slave nodes to balance load and enhance performance.

## Project Structure
- Client.py: Manages the interaction of clients initiating READ and WRITE requests.
- Master.py: Coordinates all operations between clients and slaves, maintaining lists of active slaves and keys.
- Slave.py: Handles storage and processing of data, sending ACK bits to the master after operations.

## File Details

### Client.py

#### Functionality
Manages client interactions, allowing users to issue READ and WRITE commands.

#### Process
  - Connects to the master via a socket.
  - Sends commands based on user input and displays responses from the master.

### Master.py 

#### Functionality
master.py serves as the central coordinator for the distributed shared memory system. Its primary roles include managing connections, handling client requests, and maintaining a consistent view of the data across the system.

#### Process
- *Connection Management:* The master listens on a specified port for incoming connections from both clients and slaves. Upon establishing a connection, it identifies the type of connection (client or slave) based on the initial message received.
  
- *Handling WRITE Operations:*
  - When a WRITE request is received from a client, the master selects a subset of slave nodes to handle the operation. This subset selection is based on a hash function that aims to distribute the load evenly across available slaves.
  - The master sends the WRITE command along with the data to the chosen slaves and waits for ACK bits to confirm that the operation has been successfully completed.
  - If ACK bits are not received from any slave within a specified timeout, the master assumes the slave has failed and removes it from the list of active slaves. This ensures that only responsive and reliable slaves are used for future operations.

- *Handling READ Operations:*
  - For READ requests, the master checks its records to determine which slaves last stored the data associated with the requested key.
  - It retrieves the value from one of these slaves. If multiple writes have occurred, the value retrieved is the one from the most recent successful write, ensuring that the client always receives the latest data.
  - It attempts to retrieve the value from one of these slaves. If the initial attempt fails to receive a response (e.g., due to a slave failure or network issues), the master employs a continuous pinging mechanism. This process involves repeatedly sending the READ request until a response is received.
  - If the key is not found in any slave (e.g., if all slaves that stored the key have failed), the master responds with a "NOT_FOUND" message.

- *Backup Master:* 
  - When the primary master fails, all the slaves and clients connect to the backup master.
  - Write operations continue to function as usual. 
  - However, for read operations, the backup master first checks if the requested keys are present in the key_to_slaves dictionary. If so, read requests are only sent to the slaves specified for those keys. 
  - If the keys are not present in the dictionary, the backup master sends read requests to all the slaves, collects the responses, determines the majority response, and updates the key_to_slaves dictionary accordingly.

#### Data Consistency and Fault Tolerance
- *Consistency:* The master plays a crucial role in maintaining data consistency. By keeping track of which slaves have stored which keys and ensuring that READ operations always return the latest write value, the master ensures that the system behaves coherently across multiple nodes.
- *Fault Tolerance:* The use of ACK bits allows the master to monitor the health and responsiveness of slave nodes. Non-responsive slaves are quickly identified and excluded from future operations, which helps in maintaining the overall robustness of the system.

### Slave.py

#### Functionality
Stores data and processes requests from the master.

#### Process
  - Registers with the master and waits for commands.
  - On receiving a WRITE command, stores the provided data and sends an ACK bit back to the master.
  - On receiving a READ command, retrieves and sends the requested data back to the master.

## Running the System
Open separate terminals for each component and use the following commands to simulate a distributed environment:

```py 
python3 Master.py
```

### Open a new terminal for each slave instance
```py
python3 Slave.py
```

### Open a new terminal for each client instance
```py
python Client.py
```

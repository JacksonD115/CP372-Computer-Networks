import socket
import os
import datetime
import threading

MAX_CLIENTS = 3
clients = {}  # Stores {client_name: (connect_time, disconnect_time)}

def handle_client(client_socket, client_address, client_id):
    """Handles a single client connection."""
    client_name = f"Client{client_id:02d}"  # Formats the clients as Client01, Client02 etc
    connect_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clients[client_name] = (connect_time, None)  # Store only name as key

    print(f"{client_name} connected from {client_address} at {connect_time}")

    # Send welcome message
    client_socket.send(f"Welcome {client_name}! Type 'STATUS' to see other clients, 'LIST_FILES' to list files, 'GET_FILE <filename>' to receive a file, or 'exit' to disconnect.".encode())

    while True:
        try:
            data = client_socket.recv(1024).decode()
            if not data:
                break

            print(f"Received from {client_name}: {data}")

            if data.lower() == "exit":
                print(f"{client_name} disconnected.")
                break

            elif data.lower() == "status":
                status_message = "Connected clients:\n"
                for name, (connect_time, disconnect_time) in clients.items():
                    status_message += f"{name} - Connected at {connect_time}"
                    if disconnect_time:
                        status_message += f", Disconnected at {disconnect_time}"
                    status_message += "\n"
                client_socket.send(status_message.encode())

            elif data.lower() == "list_files":
                files = os.listdir('.')  # List files in the current directory
                print(f"Server Files: {files}")  # Debugging: Print files
                file_list = "\n".join(files) if files else "No files available."
                client_socket.send(file_list.encode())

            elif data.lower().startswith("get_file "):
                filename = data.split(" ", 1)[1]
                if os.path.exists(filename):
                    client_socket.send("START".encode())
                    with open(filename, "rb") as file:
                        while file_chunk := file.read(1024):
                            client_socket.send(file_chunk)
                    client_socket.send("END".encode())
                else:
                    client_socket.send("File not found.".encode())

            else:
                client_socket.send(f"{data} ACK".encode())

        except ConnectionResetError:
            break

    
    disconnect_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if client_name in clients:
        clients[client_name] = (clients[client_name][0], disconnect_time)

    client_socket.close()

def initialize_server():
    """Initializes the server and handles multiple clients."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 54321))
    server_socket.listen(MAX_CLIENTS)
    print("Server started, waiting for connections...")

    client_id = 1 

    while True:
        if len(clients) < MAX_CLIENTS:
            client_socket, client_address = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket, client_address, client_id)).start()
            client_id += 1
        else:
            print("Maximum clients reached. New connections will be refused.")

if __name__ == "__main__":
    initialize_server()

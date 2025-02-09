import socket
def initialize_client():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("127.0.0.1", 54321))

        print(client_socket.recv(1024).decode())

        while True:
            message = input("Enter a command or message: ")
            if not message:
                continue

            client_socket.send(message.encode())

            if message.lower() == "exit":
                print("Disconnected from server.")
                break
            
            response = client_socket.recv(4096).decode()

            if response == "START":
                print("Receiving file...")
                with open("received_file.txt", "wb") as file:
                    while True:
                        file_chunk = client_socket.recv(1024)
                        if file_chunk == b"END":
                            break
                        file.write(file_chunk)
                print("File transfer complete.")
            else:
                print(f"Server Response:\n{response}")
        
        client_socket.close()
    except ConnectionRefusedError:
        print("Server is unvavailable.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    initialize_client()

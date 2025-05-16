import socket
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import time

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000

clients = set()
canvas_state = []  # Store the canvas state as a list of drawing actions

canvas_state_lock = Lock()

def handle_client(client_socket):
    try:
        while True:
            data = client_socket.recv(1024).decode()
            # Check if the client requested the canvas state
            if data == "REQUEST_CANVAS_STATE":
                # Send the entire canvas state to the client
                with canvas_state_lock:
                    for action in canvas_state:
                        client_socket.sendall(action)
                        time.sleep(0.0001)
            elif data:
                # Received a new drawing action from the client
                action = data.encode()  # Ensure it's in bytes
                with canvas_state_lock:
                    canvas_state.append(action)
                broadcast(action)
            else:
                break
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        with canvas_state_lock:
            if client_socket in clients:
                clients.remove(client_socket)
        client_socket.close()

def broadcast(data):
    for client in clients.copy():
        if client.fileno() == -1:  # Check if the client socket is still valid
            clients.remove(client)
            continue
        try:
            client.sendall(data)
        except Exception as e:
            print(f"Error broadcasting to client: {e}")
            clients.remove(client)

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)

    print(f"[*] Server listening on {SERVER_HOST}:{SERVER_PORT}")

    with ThreadPoolExecutor(max_workers=10) as executor:
        try:
            while True:
                client_socket, addr = server_socket.accept()
                clients.add(client_socket)
                print(f"Accepted connection from {addr}")
                executor.submit(handle_client, client_socket)
        except KeyboardInterrupt:
            print("Server shutting down...")
            server_socket.close()

if __name__ == "__main__":
    start_server()
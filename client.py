import socket
import threading
import tkinter as tk
from tkinter import Canvas
import tkinter.colorchooser as colorchooser
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000

def receive_messages(sock, canvas):
    while True:
        data = sock.recv(1024)
        if not data:
            break

        if data == b'':
            break

        try:
            x, y, color = data.decode().split(',')
            x, y = int(x), int(y)
            canvas.create_line(x, y, x, y, width=5, capstyle=tk.ROUND, smooth=tk.TRUE, fill=color)
        except ValueError:
            pass

def on_mouse_drag(event, sock,draw_color):
    x, y = event.x, event.y
    message = f"{x},{y},{draw_color}".encode()
    sock.send(message)

def pick_color():
    # This function will open a color picker dialog and return the selected color.
    color_code = colorchooser.askcolor(title="Choose color")
    return color_code[1] if color_code[1] else 'black'  # Default to black if no color is selected

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    client_socket.send(b'REQUEST_CANVAS_STATE')
    root = tk.Tk()
    root.title("Shared Canvas")

    canvas = Canvas(root, width=800, height=600, bg="white")
    canvas.pack()

    draw_color = 'black'

    # Add a button to pick color
    color_button = tk.Button(root, text="Pick Color", command=lambda: update_color())
    color_button.pack()

    def update_color():
        nonlocal draw_color
        chosen_color = pick_color()
        if chosen_color:
            draw_color = chosen_color

    canvas.bind("<B1-Motion>", lambda event: on_mouse_drag(event, client_socket, draw_color))

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket, canvas))
    receive_thread.start()

    root.mainloop()
if __name__ == "__main__":
    start_client()

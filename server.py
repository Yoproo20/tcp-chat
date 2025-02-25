import socket
import threading
import re
import time

# Variables
HOST = '0.0.0.0'
PORT = 49152 
PASSWORD = "nopassword" 
clients = [] 
lock = threading.Lock()

def clean_username(name):
    return re.sub(r'[^\w-]', '', name.replace(' ', '_'))[:20] or "Anonymous"

def broadcast(message, sender=None):
    global clients
    print("[LOG] " + message.strip())
    lock.acquire()
    for client in clients:
        if client != sender:
            client[0].send(message.encode())
    lock.release()

def handle_client(client_sock, addr):
    global clients
    username = None
    print("[CONNECT] " + str(addr))
    
    # Authentication
    client_sock.send(b"Enter password: ")
    password = client_sock.recv(1024).decode().strip()
    if password != PASSWORD:
        client_sock.send(b"Auth failed\n")
        client_sock.close()
        return
    
    # Get username
    client_sock.send(b"Enter username: ")
    username = clean_username(client_sock.recv(1024).decode().strip())
    print("[USERNAME] " + str(addr) + " -> " + username)
    
    lock.acquire()
    clients.append((client_sock, username))
    lock.release()
    
    broadcast(username + " joined\n")
    client_sock.send(("Welcome " + username + "\n").encode())
    
    # Message loop
    while True:
        msg = client_sock.recv(1024).decode().strip()
        if not msg or msg.lower() == 'exit':
            break
        broadcast(username + " - " + msg + "\n", sender=client_sock)
    
    lock.acquire()
    if (client_sock, username) in clients:
        clients.remove((client_sock, username))
    lock.release()
    
    broadcast(username + " left\n")
    client_sock.close()
    print("[DISCONNECT] " + username)

def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(5)
    print("Server started on " + HOST + ":" + str(PORT))
    
    while True:
        client, addr = sock.accept()
        threading.Thread(target=handle_client, args=(client, addr)).start()

start_server()

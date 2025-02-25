import socket
import threading

HOST = '127.0.0.1' 
PORT = 49152 
running = True

def recv_thread(sock):
    global running
    while running:
        data = sock.recv(1024).decode()
        if not data:
            break
        print(f"\r{data}\n> ", end='', flush=True)

def start_client(): 
    global running
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT)) 
    
    print(sock.recv(1024).decode(), end='')
    sock.send(input().encode())
    
    print(sock.recv(1024).decode(), end='')
    sock.send(input().encode())
    
    threading.Thread(target=recv_thread, args=(sock,)).start()
    
    # Input loop
    print("\nConnected (type 'exit' to quit)")
    while True:
        print("> ", end='', flush=True)
        msg = input()
        sock.send(msg.encode())
        if msg.lower() == 'exit':
            running = False
            break
    
    sock.close()

start_client()

import socket
import threading

HOST = '0.0.0.0'
PORT = 12345

clients = []
clients_lock = threading.Lock()

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    try:
        while True:
            data = conn.recv(1024)
            if data:
                broadcast(data, conn)
            else:
                break
    except ConnectionResetError:
        pass
    finally:
        with clients_lock:
            if conn in clients:
                clients.remove(conn)
        conn.close()
        print(f"[DISCONNECTED] {addr} disconnected.")

def broadcast(message: bytes, source_conn):
    with clients_lock:
        for client in clients[:]:
            if client != source_conn:
                try:
                    client.send(message)
                except:
                    clients.remove(client)
                    client.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        with clients_lock:
            clients.append(conn)
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == '__main__':
    start_server()

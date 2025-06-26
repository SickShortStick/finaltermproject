import socket
import threading

HOST = '0.0.0.0'
PORT = 12345

clients = {}
clients_lock = threading.Lock()

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    try:
        username = conn.recv(1024).decode().strip()
        if not username:
            print(f"[ERROR] No username received from {addr}. Closing connection.")
            conn.close()
            return
        
        with clients_lock:
            clients[username] = conn

        while True:
            data = conn.recv(1024)
            if data:
                try:
                    recipient, msg = data.decode().split(":", 1)
                    print(f"[MESSAGE] {username} to {recipient.strip()}: {msg.strip()}")
                    send_to_user(recipient.strip(), f"{username}: {msg.strip()}")
                except Exception as e:
                    print(f"[ERROR] {e}")
            else:
                break
    except ConnectionResetError:
        pass
    finally:
        with clients_lock:
            for user, sock in list(clients.items()):
                if sock == conn:
                    del clients[user]
        conn.close()
        print(f"[DISCONNECTED] {addr} disconnected.")

def send_to_user(username, message):
    with clients_lock:
        if username in clients:
            try:
                clients[username].send(message.encode())
            except:
                clients[username].close()
                del clients[username]


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == '__main__':
    start_server()

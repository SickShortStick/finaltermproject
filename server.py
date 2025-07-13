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

        message_buffer = b''
        
        while True:
            try:
                data = conn.recv(8192)
                if not data:
                    break
                
                message_buffer += data
                
                while True:
                    try:
                        decoded = message_buffer.decode()
                        
                        if "<img>" in decoded:
                            parts = decoded.split(":")
                            if len(parts) >= 4:
                                recipient = parts[0].strip()
                                filename = parts[2].strip()
                                size = int(parts[3].strip())
                                
                                print(f"[IMAGE HEADER] From {username} to {recipient}: {filename} ({size} bytes)")
                                
                                message_buffer = b''
                                
                                image_data = b''
                                while len(image_data) < size:
                                    chunk = conn.recv(min(8192, size - len(image_data)))
                                    if not chunk:
                                        raise ConnectionError("Connection lost during image transfer")
                                    image_data += chunk
                                
                                forward_image(recipient, f"{username}:<img>:{filename}:{size}".encode(), image_data)
                                break
                            else:
                                break
                        else:
                            if ":" in decoded:
                                recipient, msg = decoded.split(":", 1)
                                print(f"[MESSAGE] {username} to {recipient.strip()}: {msg.strip()}")
                                send_to_user(recipient.strip(), f"{username}: {msg.strip()}")
                                message_buffer = b''
                                break
                            else:
                                break
                    except UnicodeDecodeError:
                        break
                    except ValueError as e:
                        print(f"[ERROR] Message parsing error: {e}")
                        message_buffer = b''
                        break
                        
            except Exception as e:
                print(f"[ERROR] {e}")
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


def forward_image(recipient, header_bytes, image_bytes):
    with clients_lock:
        if recipient in clients:
            try:
                clients[recipient].sendall(header_bytes)
                clients[recipient].sendall(image_bytes)
                print(f"[FORWARDED IMAGE] Sent image to {recipient} ({len(image_bytes)} bytes)")
            except (ConnectionResetError, BrokenPipeError, OSError) as e:
                print(f"[ERROR] Failed to send image to {recipient}: {e}")
                try:
                    clients[recipient].close()
                except:
                    pass
                del clients[recipient]
            except Exception as e:
                print(f"[ERROR] Unexpected error sending image to {recipient}: {e}")
                try:
                    clients[recipient].close()
                except:
                    pass
                del clients[recipient]
        else:
            print(f"[WARNING] Recipient {recipient} not found in clients")



def send_to_user(username, message):
    with clients_lock:
        if username in clients:
            try:
                encoded_message = message.encode('utf-8')
                clients[username].sendall(encoded_message)
                print(f"[SENT] Message to {username}: {message[:50]}...")
            except (ConnectionResetError, BrokenPipeError, OSError) as e:
                print(f"[ERROR] Failed to send message to {username}: {e}")
                try:
                    clients[username].close()
                except:
                    pass
                del clients[username]
            except Exception as e:
                print(f"[ERROR] Unexpected error sending to {username}: {e}")
                try:
                    clients[username].close()
                except:
                    pass
                del clients[username]
        else:
            print(f"[WARNING] User {username} not found in clients")

def update_client_username(old_username, new_username):
    with clients_lock:
        if old_username in clients:
            clients[new_username] = clients.pop(old_username)
            print(f"[USERNAME CHANGE] Updated {old_username} to {new_username}")


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

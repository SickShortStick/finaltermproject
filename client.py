import socket
import threading

HOST = '127.0.0.1'
PORT = 12345

def receive_loop(sock):
    try:
        while True:
            msg = sock.recv(1024)
            if msg:
                print(msg.decode())
            else:
                print("Disconnected from server.")
                break
    except Exception as e:
        print(f"Error receiving data: {e}")
    finally:
        sock.close()

def start_client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    print(f"Connected to server {HOST}:{PORT}")

    recv_thread = threading.Thread(target=receive_loop, args=(sock,), daemon=True)
    recv_thread.start()

    try:
        while True:
            message = input()
            if message.lower() == "exit":
                print("Exiting...")
                break
            sock.send(message.encode())
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        sock.close()

if __name__ == "__main__":
    start_client()
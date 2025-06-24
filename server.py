import socket


HOST = '0.0.0.0'
PORT = 12345


def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.bind((HOST, PORT))
        srv.listen()
        print(f'server running on {HOST}:{PORT}')
        conn, addr = srv.accept()
        with conn:
            print(f'connected to {addr}')
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(data)

if __name__ == '__main__':
    run_server()

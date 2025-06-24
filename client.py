import socket


HOST = '127.0.0.1'
PORT = 12345


def run_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cli:
        cli.connect((HOST, PORT))
        while True:
            msg = input('message: ')
            if msg.lower() == 'exit':
                break
            cli.sendall(msg.encode('utf-8'))
            reply = cli.recv(1024).decode('utf-8')
            print("server replied: ", reply)

if __name__ == '__main__':
    run_client()
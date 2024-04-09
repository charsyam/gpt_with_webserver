import socket

def handle_request(client_socket):
    """Handles a single client request."""
    request = client_socket.recv(1024)
    print(f'Received: {request.decode("utf-8")}')
    
    http_response = """\
HTTP/1.1 200 OK

Hello, world!
"""
    client_socket.sendall(http_response.encode())

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', 8000))
    server_socket.listen(5)
    print("Serving HTTP on port 8000...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Accepted connection from {addr}")
        handle_request(client_socket)
        client_socket.close()

if __name__ == '__main__':
    main()


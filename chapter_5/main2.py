import socket
import os

def receive_http_request(client_socket):
    """Receives the complete HTTP request from the client."""
    request_data = bytearray()
    while True:
        chunk = client_socket.recv(1024)
        request_data += chunk
        if b"\r\n\r\n" in request_data:  # End of headers detected
            break
    return request_data.decode('utf-8')

def parse_http_request(request_text):
    """Parses the HTTP request to get the method and path."""
    lines = request_text.splitlines()
    if lines:
        request_line = lines[0]
        method, path, _ = request_line.split(maxsplit=2)
        return method, path
    return None, None

def serve_file(client_socket, filepath):
    """Serves a file by sending its contents over the socket."""
    if not os.path.isfile(filepath):
        # File not found, send 404 response
        response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\nFile not found."
        client_socket.sendall(response.encode())
    else:
        # File found, send 200 response and file content
        client_socket.sendall("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n".encode())
        with open(filepath, 'rb') as f:
            client_socket.sendfile(f)
        client_socket.sendall("\r\n".encode())  # End of file marker

def handle_request(client_socket):
    """Handles a single client request."""
    request_text = receive_http_request(client_socket)
    method, path = parse_http_request(request_text)

    # Serving files from a directory named 'www'
    if method == 'GET':
        base_directory = 'www'
        if path == '/':
            path = '/index.html'  # Default file to serve
        filepath = os.path.join(base_directory, path.strip('/'))
        serve_file(client_socket, filepath)
    else:
        # Method not allowed
        response = "HTTP/1.1 405 Method Not Allowed\r\nContent-Type: text/plain\r\n\r\nThis server only supports GET requests."
        client_socket.sendall(response.encode())

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


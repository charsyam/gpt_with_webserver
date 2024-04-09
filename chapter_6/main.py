import socket
import os
import urllib.parse

def receive_http_request(client_socket):
    """Receives the complete HTTP request from the client."""
    request_data = bytearray()
    while True:
        chunk = client_socket.recv(1024)
        request_data += chunk
        if b"\r\n\r\n" in request_data:  # End of headers detected
            break
    content_length = 0
    for line in request_data.split(b'\r\n'):
        if line.startswith(b'Content-Length: '):
            content_length = int(line.split(b': ')[1])
            break
    while len(request_data) - request_data.find(b'\r\n\r\n') - 4 < content_length:
        request_data += client_socket.recv(1024)
    return request_data.decode('utf-8')

def parse_http_request(request_text):
    """Parses the HTTP request to get the method, path, and body (if any)."""
    request_line, headers_body = request_text.split('\r\n', 1)
    headers, _, body = headers_body.partition('\r\n\r\n')
    method, path, _ = request_line.split(maxsplit=2)
    return method, path, body

def handle_get_request(client_socket, path):
    """Handles GET requests."""
    base_directory = 'www'
    if path == '/':
        path = '/index.html'  # Default file to serve
    filepath = os.path.join(base_directory, path.strip('/'))
    if not os.path.isfile(filepath):
        response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\nFile not found."
        client_socket.sendall(response.encode())
    else:
        client_socket.sendall("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n".encode())
        with open(filepath, 'rb') as f:
            client_socket.sendfile(f)
        client_socket.sendall("\r\n".encode())

def handle_post_request(client_socket, path, body):
    """Handles POST requests."""
    # Example of processing POST data
    print(f"POST request to {path} with body: {body}")
    # Decode and parse POST data
    post_data = urllib.parse.parse_qs(body)
    print("Parsed POST data:", post_data)
    
    # Here you would typically process the data and potentially
    # respond based on the result of that processing.
    response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nPOST request processed."
    client_socket.sendall(response.encode())

def handle_request(client_socket):
    """Handles a single client request."""
    method, path, body = parse_http_request(receive_http_request(client_socket))
    
    if method == 'GET':
        handle_get_request(client_socket, path)
    elif method == 'POST':
        handle_post_request(client_socket, path, body)
    else:
        response = "HTTP/1.1 405 Method Not Allowed\r\nContent-Type: text/plain\r\n\r\nThis server only supports GET and POST requests."
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


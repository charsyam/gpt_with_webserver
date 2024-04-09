import socket

def parse_http_headers(request):
    """Parses HTTP request headers and returns a dictionary of headers."""
    headers = {}
    lines = request.splitlines()
    for line in lines[1:]:  # Skip the request line
        if line:  # Header lines will be non-empty
            header, value = line.split(": ", 1)
            headers[header] = value
        else:  # An empty line indicates the end of the headers
            break
    return headers

def handle_request(client_socket):
    """Handles a single client request."""
    request_data = client_socket.recv(1024)
    request_text = request_data.decode('utf-8')
    print(f'Received:\n{request_text}')

    # Parse headers
    headers = parse_http_headers(request_text)
    for header, value in headers.items():
        print(f'{header}: {value}')

    # Prepare and send the HTTP response
    http_response = """\
HTTP/1.1 200 OK

Hello, world! This server understands your headers!
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


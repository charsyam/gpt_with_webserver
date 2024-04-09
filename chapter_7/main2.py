import socket
import os
import re
from urllib.parse import unquote_plus

def receive_http_request(client_socket):
    """Receives the complete HTTP request from the client, handling large requests."""
    request_data = bytearray()
    content_length = 0
    while True:
        chunk = client_socket.recv(1024)
        request_data += chunk
        if b"\r\n\r\n" in request_data and content_length == 0:  # Headers received
            # Extract Content-Length for further reading if necessary
            match = re.search(b'Content-Length: (\d+)', request_data)
            if match:
                content_length = int(match.group(1))
            else:  # No Content-Length, assume all data received
                break
        # Check if we've received all data
        headers_body_split = request_data.find(b"\r\n\r\n")
        if headers_body_split != -1 and len(request_data) - headers_body_split - 4 >= content_length:
            break
    return request_data.decode('latin1')  # Decoding as 'latin1' to preserve binary data

def parse_http_request(request_data):
    """Parses the HTTP request."""
    headers, body = request_data.split('\r\n\r\n', 1)
    request_line, headers = headers.split('\r\n', 1)
    method, path, _ = request_line.split(' ', 2)
    
    # Parsing headers into a dict
    header_lines = headers.split('\r\n')
    headers = {key.lower(): value for key, value in (line.split(': ', 1) for line in header_lines)}
    
    return method, path, headers, body

def save_uploaded_file(file_content, filename):
    """Saves the uploaded file."""
    uploads_dir = 'uploads'
    os.makedirs(uploads_dir, exist_ok=True)
    filepath = os.path.join(uploads_dir, filename)
    with open(filepath, 'wb') as file:
        file.write(file_content)
    print(f"Saved file: {filepath}")

def handle_post_request(client_socket, headers, body):
    """Handles POST requests, differentiating between form data and file uploads."""
    content_type = headers.get('content-type')
    
    if content_type.startswith('multipart/form-data'):
        boundary = content_type.split('boundary=')[1]
        parts = body.split(f'--{boundary}')
        for part in parts:
            if 'Content-Disposition: form-data;' in part:
                # Extracting the name field
                name_match = re.search(r'name="([^"]+)"', part)
                filename_match = re.search(r'filename="([^"]+)"', part)
                if filename_match:
                    filename = unquote_plus(filename_match.group(1))
                    file_content_start = part.index('\r\n\r\n') + 4
                    file_content_end = part.rfind('\r\n')
                    file_content = part[file_content_start:file_content_end].encode('latin1')
                    save_uploaded_file(file_content, filename)
                elif name_match:
                    value_start = part.index('\r\n\r\n') + 4
                    value_end = part.rfind('\r\n')
                    value = part[value_start:value_end]
                    print(f"Received form field {name_match.group(1)} with value: {value}")

        response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nPOST request processed."
    else:
        # Handling other content types, e.g., application/x-www-form-urlencoded
        print("Received POST data:", body)
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nPOST data received."
    
    client_socket.sendall(response.encode())

def handle_request(client_socket):
    """General request handling, routing to the appropriate function based on the method."""
    request_data = receive_http_request(client_socket)
    method, path, headers, body = parse_http_request(request_data)
    
    if method == 'POST':
        handle_post_request(client_socket, headers, body)
    else:
        # Add handling for GET or other methods as needed
        response = "HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\n\r\nUnsupported operation."
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


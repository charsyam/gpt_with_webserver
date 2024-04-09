import socket
import os
import re
from urllib.parse import unquote_plus

def save_uploaded_file(file_content, filename):
    """Saves the uploaded file to the 'uploads' directory."""
    uploads_dir = 'uploads'
    os.makedirs(uploads_dir, exist_ok=True)
    filepath = os.path.join(uploads_dir, filename)
    with open(filepath, 'wb') as f:
        f.write(file_content)
    print(f"File saved to {filepath}")

def parse_multipart_data(data, boundary):
    """Parses multipart/form-data request body."""
    # Split the data into parts on the boundary
    parts = data.split(f'--{boundary}')
    file_content = None
    filename = None
    for part in parts:
        # If "Content-Disposition" in part, it might have a file
        if "Content-Disposition: form-data;" in part:
            # Extract filename
            filename_match = re.search(r'filename="([^"]+)"', part)
            if filename_match:
                filename = unquote_plus(filename_match.group(1))
                # Extract the file content
                file_content_start = part.index('\r\n\r\n') + 4
                file_content_end = part.rfind('\r\n')
                file_content = part[file_content_start:file_content_end].encode('latin1')
                break  # Assuming one file for simplicity
    return filename, file_content

def handle_post_request(client_socket, boundary, data):
    """Handles POST request including file upload."""
    filename, file_content = parse_multipart_data(data, boundary)
    if filename and file_content:
        save_uploaded_file(file_content, filename)
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nFile uploaded successfully."
    else:
        response = "HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\n\r\nFailed to upload file."
    client_socket.sendall(response.encode())

def parse_http_request(request_data):
    """Parses the HTTP request to extract relevant information for file upload."""
    headers, body = request_data.split('\r\n\r\n', 1)
    headers_lines = headers.split('\r\n')
    method, path, _ = headers_lines[0].split(' ', 2)
    # Look for Content-Type header to extract boundary
    boundary = None
    for line in headers_lines:
        if line.startswith('Content-Type: multipart/form-data;'):
            boundary = line.split('boundary=')[1]
            break
    return method, path, boundary, body

def receive_http_request(client_socket):
    """Receives the complete HTTP request from the client."""
    request_data = bytearray()
    while True:
        chunk = client_socket.recv(1024)
        request_data += chunk
        if b"\r\n\r\n" in request_data and b"Content-Length: " not in request_data:
            break  # Simple check for end of headers if Content-Length is missing
    return request_data.decode('latin1')  # Use 'latin1' to preserve binary data of file

def handle_request(client_socket):
    """Handles incoming HTTP requests."""
    request_data = receive_http_request(client_socket)
    method, path, boundary, body = parse_http_request(request_data)
    
    if method == 'POST' and boundary:
        handle_post_request(client_socket, boundary, body)
    else:
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

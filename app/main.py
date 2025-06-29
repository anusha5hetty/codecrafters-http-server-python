import socket  # noqa: F401
import threading

from pathlib import Path
import argparse
current_dir = Path(__file__).parent.resolve()

tmp_dir = Path(f"{current_dir}\\..\\tmp")

def ok_response(message: str = None, content_type = 'text/plain') -> str:
    """Returns a simple HTTP 200 OK response."""
    if message and len(message) > 0:
        msg_len = len(message)
        # response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body><h1>Hello, World!</h1></body></html>"
        return f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\nContent-Length: {msg_len}\r\n\r\n{message}"
    return "HTTP/1.1 200 OK\r\n\r\n"

def not_found_response() -> str:
    """Returns a simple HTTP 404 Not Found response."""
    return "HTTP/1.1 404 Not Found\r\n\r\n"

def server_error_response() -> str:
    """Returns a simple HTTP 404 Not Found response."""
    return "HTTP/1.1 500 Internal Server Error\r\n\r\n"

def get_headers(request_text: str) -> dict:
    """Parses the HTTP request headers from the request text."""
    # EG: GET /user-agent HTTP/1.1\r\nUser-Agent: PostmanRuntime/7.44.1\r\nAccept: */*\r\nCache-Control: no-cache\r\nPostman-Token: 16311131-6e67-4a59-ae78-9a052d4667df\r\nHost: localhost:4221\r\nAccept-Encoding: gzip, deflate, br\r\nConnection: keep-alive\r\n\r\n
    headers = {}
    lines = request_text.splitlines() # ['GET /user-agent HTTP/1.1', 'User-Agent: PostmanRuntime/7.44.1', 'Accept: */*', 'Cache-Control: no-cache']
    headers_req_string =lines[1:] # Skip the request line (the first line 'GET /user-agent HTTP/1.1')
    for header_line in headers_req_string:  # Skip the request line
        if header_line.strip() == "":
            break  # Stop at the first empty line
        key, value = header_line.split(":", 1)
        headers[key.strip()] = value.strip()
    return headers

def get_file_content(file_path: Path) -> str:
    file_content = ""
    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()
    return file_content

def get_file_path(directory: Path, filename: str) -> list:
    """Recursively search for a file in a directory and return all matches."""
    matches = []
    for file_path in directory.rglob(filename):
        if file_path.is_file():
            matches.append(file_path)
    return matches

def handle_file_read(file_name: str, directory_name: str) -> str:
    """Reads the content of a file and returns it as a string."""
    # file_path = Path(current_dir2, file_name)
    tmp_dir = Path(current_dir, directory_name)
    try:
        print(f"Looking for file: {file_name} in directory: {tmp_dir}")
        lst_file_paths = get_file_path(tmp_dir, file_name)
        print(f"Found file paths: {lst_file_paths}")
        if lst_file_paths:
            file_content = get_file_content(lst_file_paths[0])
            return ok_response(file_content, 'application/octet-stream')
        else:
            print(f"File not found: {file_name}")
            return not_found_response()
    except Exception as e:
        print(f"Error reading file {file_name}: {e}")
        return server_error_response()

def routing(request_path, request_text, args):
    headers = get_headers(request_text)
    if request_path.startswith("/index.html") or request_text.startswith("GET / HTTP"):
        # If the request is a GET /index.html, send a response
        print("Received index request")
        response = ok_response()
    elif request_path.startswith("/echo"):
        # If the request is a GET /echo/abc, send a response with the message "abc"
        print("Received echo request")
        text_to_echo = request_path.split("/echo/")[1]  # 'abc'
        response = ok_response(text_to_echo)
    elif request_path.startswith("/user-agent"):
        # If the request is a GET /user-agent, send a response with the User-Agent header value
        print("Received user-agent request")
        user_agent = headers.get("User-Agent", "Unknown")
        response = ok_response(user_agent)
    elif request_path.startswith("/files"):
        file_name = request_path.split("/files/")[1]
        response = handle_file_read(file_name, args.directory)
    else:
        # For any other request, send a 404 Not Found response
        print("Received unknown request")
        response = not_found_response()
    return response

def handle_client(client_socket, args):
    try:
        # Receive up to 1024 bytes from the client
        # You can ignore the headers for now. You'll learn about parsing headers in a later stage.
        # In this stage, the request target is written as a URL path. But the request target actually has four possible formats. The URL path format is called the "origin form," and it's the most commonly used format. The other formats are used for more niche scenarios, like sending a request through a proxy.
        # For more information about HTTP requests, see the MDN Web Docs on HTTP requests or the HTTP/1.1 specification.
        # Simulate some delay for the client to connect
        request_bytes = client_socket.recv(1024)
        request_text = request_bytes.decode("utf-8")
        print("Received request:")
        print(request_text)

        request_route = request_text.splitlines()[0] #'GET /echo/abc HTTP/1.1'
        request_path = request_route.split(" ")[1] # 'The path example - /echo/abc'
        
        # Decides on which response to send based on the request path
        print(f"Request path: {request_path}")
        response = routing(request_path, request_text, args)  # Call the routing function with the path and headers
            # response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\nNot Found"
        client_socket.send(response.encode())
        print("Stop")
        # server_socket.accept()[0].send("HTTP/1.1 200 OK\r\n\r\n".encode()) # send response
    except Exception as e:
        print(f"An error occurred: {e}")
        # Optionally, you can send an error response back to the client
        error_response = not_found_response()
        client_socket.send(error_response.encode())
    finally:
        # Close the client socket after handling the request
        client_socket.close()
        print("Client connection closed")

def main(args):
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221))
    # server_socket.accept() # wait for client
    while True:
        try:
            # Accept a new client connection
            client_socket, address = server_socket.accept()
            print(f"New connection from {address}")
            # accepted_request would contain a tuple (client_socket, address)
            # accepted_request[0] would contain the object <socket.socket fd=888, family=2, type=1, proto=0, laddr=('127.0.0.1', 4221), raddr=('127.0.0.1', 59883)>
            # accepted_request[1] would contain the return address of the client, e.g. ('127.0.0.1', 59883)
            
            client_thread = threading.Thread(target=handle_client, args=(client_socket, args)) # Start a new thread to handle the client request
            client_thread.daemon = True  # Set the thread as a daemon so it will exit when the main program exits
            client_thread.start()  # Start the thread to handle the client request

            # The `daemon` property controls how threads behave when the main program exits:

            # ## `daemon=True` (Daemon Thread)
            # - **Dies automatically** when the main program exits
            # - **Non-blocking**: Main program doesn't wait for daemon threads to finish
            # - **Background tasks**: Used for tasks that should stop when the program stops
            # - **Example**: Cleanup tasks, monitoring, logging

            # ## `daemon=False` (Non-Daemon Thread) 
            # - **Keeps running** even after main program tries to exit
            # - **Blocking**: Main program waits for all non-daemon threads to finish before exiting
            # - **Critical tasks**: Used for important work that must complete
            # - **Example**: File processing, database transactions

            # ## In Your Code:
            # ````python
            # client_thread.daemon = True  # Daemon thread
            # client_thread.start()
            # ````

            # **With `daemon=True`**: If you press Ctrl+C or the main program ends, all client handler threads will immediately stop, and the server will exit cleanly.
            # **With `daemon=False`**: The server would wait for all active client connections to finish processing before it could exit, potentially hanging if clients don't disconnect properly.

            # For a web server handling client requests, `daemon=True` is usually preferred because you want the server to shut down immediately when requested, rather than waiting for all connections to finish
        except KeyboardInterrupt:
            print("Server shutting down...")
            break
    server_socket.close()
    print("Server socket closed. Exiting...")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='HTTP Server')
    parser.add_argument('--directory', type=str, default="", required=False,
                       help='Directory to serve files from')
    return parser.parse_args()

if __name__ == "__main__":
    parsed_args = parse_arguments()
    main(parsed_args)

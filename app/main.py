import socket  # noqa: F401

def ok_response(message: str = None) -> str:
    """Returns a simple HTTP 200 OK response."""
    if message and len(message) > 0:
        msg_len = len(message)
        # response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body><h1>Hello, World!</h1></body></html>"
        return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {msg_len}\r\n\r\n{message}"
    return "HTTP/1.1 200 OK\r\n\r\n"

def not_found_response() -> str:
    """Returns a simple HTTP 404 Not Found response."""
    return "HTTP/1.1 404 Not Found\r\n\r\n"

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

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221))
    # server_socket.accept() # wait for client
    accepted_request = server_socket.accept()
    # accepted_request would contain a tuple (client_socket, address)
    # accepted_request[0] would contain the object <socket.socket fd=888, family=2, type=1, proto=0, laddr=('127.0.0.1', 4221), raddr=('127.0.0.1', 59883)>
    # accepted_request[1] would contain the return address of the client, e.g. ('127.0.0.1', 59883)
    client_socket = accepted_request[0]

    # Receive up to 1024 bytes from the client
    # You can ignore the headers for now. You'll learn about parsing headers in a later stage.
    # In this stage, the request target is written as a URL path. But the request target actually has four possible formats. The URL path format is called the "origin form," and it's the most commonly used format. The other formats are used for more niche scenarios, like sending a request through a proxy.
    # For more information about HTTP requests, see the MDN Web Docs on HTTP requests or the HTTP/1.1 specification.
    request_bytes = client_socket.recv(1024)
    request_text = request_bytes.decode("utf-8")
    print("Received request:")
    print(request_text)

    request_route = request_text.splitlines()[0] #'GET /echo/abc HTTP/1.1'
    request_path = request_route.split(" ")[1] # 'The path example - /echo/abc'
    headers = get_headers(request_text)  # Parse headers if needed
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
    else:
        # For any other request, send a 404 Not Found response
        print("Received unknown request")
        response = not_found_response()
        # response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\nNot Found"
    client_socket.send(response.encode())
    print("Stop")
    # server_socket.accept()[0].send("HTTP/1.1 200 OK\r\n\r\n".encode()) # send response


if __name__ == "__main__":
    for i in range(10):
        print(f"Iteration {i + 1}")
        # You can uncomment the next line to test the server
        main()
    # main()

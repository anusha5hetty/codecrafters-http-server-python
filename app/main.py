import socket  # noqa: F401


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
    request_bytes = client_socket.recv(1024)
    request_text = request_bytes.decode("utf-8")
    if request_text.startswith("GET /index.html"):
        # If the request is a GET /index.html, send a response
        print("Received index request")
        response = "HTTP/1.1 200 OK\r\n\r\n"
        # response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body><h1>Hello, World!</h1></body></html>"
        client_socket.send(response.encode())
    else:
        # For any other request, send a 404 Not Found response
        print("Received unknown request")
        response = "HTTP/1.1 404 Not Found\r\n\r\n"
        # response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\nNot Found"
        client_socket.send(response.encode())
    print("Stop")
    # server_socket.accept()[0].send("HTTP/1.1 200 OK\r\n\r\n".encode()) # send response


if __name__ == "__main__":
    main()

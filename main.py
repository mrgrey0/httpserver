import socket  # noqa: F401
import os
import threading
import urllib.parse


def handleRequest(client_socket):
    #accepting the request
    request = client_socket.recv(1024)
    print(f"recieved request : {request}")
    request = request.decode('utf-8') # decoding the byte string so it will not have a B prefix

    # extrcting URL path
    try:
        # getting first line of the request and splitting by spaces
        request_line = request.splitlines()[0]
        method, path, _ = request_line.split()
        print(f"Url of the requst : {path}")
        print(f"Method :{method}")


        print("Extracting headers")
        headers = {}
        body_lines = []
        header_ended = False

        # Extract headers and body in one loop to avoid errors reading the body later again
        lines = request.splitlines()
        for line in lines[1:]:  # Skip the request line
            if not header_ended:
                # Check for the end of headers (an empty line)
                if line == '':
                    header_ended = True  # Mark that headers have ended
                else:
                    # Split header into key and value
                    key, value = line.split(':', 1)
                    headers[key.strip()] = value.strip()
            else:
                # Collect body lines after headers end
                body_lines.append(line)

        # Join body lines
        body = '\n'.join(body_lines)

        # Printing headers and body
        print("Headers:", headers)
        print("Body:", body)



        # handling a post request
        if path == '/submit-login':            
            # Parse the form data
            form_data = urllib.parse.parse_qs(body)
            username = form_data.get('username', [''])[0]
            password = form_data.get('password', [''])[0]
            
            print(f"Received form data - Username: {username}, Password: {password}")
            
            # Create a response (just an example, no real authentication here)
            response_body = f"<html><body><h1>Login Received</h1><p>Username: {username}</p></body></html>"
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html\r\n"
                f"Content-Length: {len(response_body)}\r\n"
                "\r\n"
                f"{response_body}"
            )

        # we got the path now lets check and send response    
        elif path == '/login':
            # we will serve an local html file ( stored on the server ) as response
            # I have kept the filename same as the request url just to make the code more dynamic

            file_path = "login.html"

            # reading the file from the memory and storing it into a local string
            try:
                if os.path.exists(file_path):
                    with open(file_path,'r') as file:
                        body = file.read()

                # sending that string as response body

                # the string contains the html code for the page from the file we have stored.
                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/html\r\n"
                    f"Content-Length: {len(body)}\r\n"
                    "\r\n"
                    f"{body}"
                )
            except Exception as e:
                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/html\r\n"
                    f"Content-Length: {len(body)}\r\n"
                    "\r\n"
                    f"{e}"
                ) 
        else :
            body = "<html><body><h1>404 Not Found</h1></body></html>"
            response = (
                "HTTP/1.1 404 Not Found\r\n"
                "Content-Type: text/html\r\n"
                f"Content-Length: {len(body)}\r\n"
                "\r\n"
                f"{body}"
            )

        client_socket.sendall(response.encode('utf-8'))

    except Exception as e:
        print(f"Error proccessing the request : {e}")

        response = "HTTP/1.1 400 Bad Request\r\n\r\n"
        client_socket.sendall(response.encode('utf-8'))

    finally:
        # Close the client socket
        client_socket.close()
def main():
    print("Logs from your program will appear here!")
    # creating server socket
    server_socket = socket.create_server(('localhost', 4221))

    while True: # loop to keep accepting the request
        # getting client socket object by accepting a connection
        client_socket, addr = server_socket.accept()

        # threading to handle concurrent connections as the above code works for one connection only. we need to handle all the connectons diffrently. so we use the concept of threading
        # we create a new thread for each recieved request. so our code will handle multiple requests at one time.

        client_thread = threading.Thread(target=handleRequest, args=(client_socket,))
        client_thread.start()

if __name__ == "__main__":
    main()

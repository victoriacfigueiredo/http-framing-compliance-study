import socket
import sys

TARGETS = {
    "backend": ("localhost", 8080),
    "nginx": ("localhost", 8081),
    "haproxy": ("localhost", 8082),
}

target = sys.argv[1]
host, port = TARGETS[target]

first_request = (
    "POST /test HTTP/1.1\r\n"
    "Host: localhost\r\n"
    "Content-Length: 5\r\n"
    "Transfer-Encoding: chunked\r\n"
    "\r\n"
    "0\r\n"
    "\r\n"
    "HELLO"
)

second_request = (
    "GET /second HTTP/1.1\r\n"
    "Host: localhost\r\n"
    "\r\n"
)

sock = socket.create_connection((host, port), timeout=5)
sock.settimeout(3)

print(f"=== Connected to {target} ===")

sock.sendall(first_request.encode("iso-8859-1"))

try:
    first_response = sock.recv(4096)
    print("\n=== First response ===")
    print(first_response.decode("iso-8859-1", errors="replace"))
except socket.timeout:
    print("\n=== First response ===")
    print("TIMEOUT: no response received")

print("\n=== Sending second request on the same TCP connection ===")

try:
    sock.sendall(second_request.encode("iso-8859-1"))
    second_response = sock.recv(4096)

    print("\n=== Second response ===")
    if second_response:
        print(second_response.decode("iso-8859-1", errors="replace"))
        print("\nRESULT: connection was reused / second request was processed or answered")
    else:
        print("No data received")
        print("\nRESULT: connection appears to have been closed")

except BrokenPipeError:
    print("BrokenPipeError")
    print("\nRESULT: connection was closed before second request")

except ConnectionResetError:
    print("ConnectionResetError")
    print("\nRESULT: connection was reset before/during second request")

except socket.timeout:
    print("TIMEOUT")
    print("\nRESULT: second request was not answered; connection may be open but unusable or waiting")

finally:
    sock.close()
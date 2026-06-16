import socket
import sys

TARGETS = {
    "traefik": ("localhost", 8084),
    "caddy": ("localhost", 8085),
}

target = sys.argv[1]
host, port = TARGETS[target]

first_request = (
    "POST /test HTTP/1.1\r\n"
    "Host: localhost\r\n"
    "X-Test-Case: RQ-012-CLTE-REUSE\r\n"
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
    "X-Test-Case: RQ-012-SECOND-REQUEST\r\n"
    "\r\n"
)

with socket.create_connection((host, port), timeout=5) as sock:
    sock.settimeout(3)

    print(f"=== Testing {target} ===")

    print("\n=== Sending first CL+TE request ===")
    sock.sendall(first_request.encode("iso-8859-1"))

    try:
        first_response = sock.recv(8192)
        print(first_response.decode("iso-8859-1", errors="replace"))
    except socket.timeout:
        print("NO FIRST RESPONSE")

    print("\n=== Sending second request on same TCP connection ===")

    try:
        sock.sendall(second_request.encode("iso-8859-1"))
        second_response = sock.recv(8192)

        if second_response:
            print(second_response.decode("iso-8859-1", errors="replace"))
            print("\nRESULT: CONNECTION REUSED")
        else:
            print("No second response")
            print("\nRESULT: CONNECTION CLOSED")

    except (BrokenPipeError, ConnectionResetError, OSError) as e:
        print(repr(e))
        print("\nRESULT: CONNECTION CLOSED")
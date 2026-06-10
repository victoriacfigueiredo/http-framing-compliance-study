import socket
import sys

TARGETS = {
    "backend": ("localhost", 8080),
    "nginx": ("localhost", 8081),
    "haproxy": ("localhost", 8082),
}

def send_raw(target_name, raw_request):
    host, port = TARGETS[target_name]

    with socket.create_connection((host, port), timeout=5) as sock:
        sock.settimeout(5)
        sock.sendall(raw_request.encode("iso-8859-1"))

        response = b""

        while True:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
            except socket.timeout:
                break

    print(response.decode("iso-8859-1", errors="replace"))

if __name__ == "__main__":
    target = sys.argv[1]

    request = (
        "GET /raw-test HTTP/1.1\r\n"
        "Host: localhost\r\n"
        "Connection: close\r\n"
        "\r\n"
    )

    send_raw(target, request)
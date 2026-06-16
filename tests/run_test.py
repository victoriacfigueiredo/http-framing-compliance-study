import socket
import csv
import json
from datetime import datetime

TARGETS = {
    "caddy": ("localhost", 8085),
}

TESTS = [

    # RQ-004
    {
        "id": "RQ-004",
        "name": "Incomplete Content-Length Body",
        "request": (
            "POST /test HTTP/1.1\r\n"
            "Host: localhost\r\n"
            "X-Test-Case: RQ-004\r\n"
            "Content-Length: 100\r\n"
            "\r\n"
            "HELLO"
        ),
        "incomplete_body_test": True,
        "expected_statuses": ["NO_STATUS", "400", "408"],
        "should_reach_backend": False,
        "expect_connection_close": True,
    }    

]


SECOND_REQUEST = (
    "GET /second HTTP/1.1\r\n"
    "Host: localhost\r\n"
    "\r\n"
)

def send_raw(host, port, raw_request, check_reuse=False, incomplete_body_test=False):
    response = b""
    second_response = b""
    connection_closed = False

    sock = socket.create_connection((host, port), timeout=5)

    if incomplete_body_test:
        sock.settimeout(8)
    else:
        sock.settimeout(3)

    try:
        sock.sendall(raw_request.encode("iso-8859-1"))

        try:
            response = sock.recv(8192)

            if not response:
                connection_closed = True

        except socket.timeout:
            if incomplete_body_test:
                connection_closed = False

        if check_reuse or incomplete_body_test:
            try:
                sock.sendall(SECOND_REQUEST.encode("iso-8859-1"))
                second_response = sock.recv(8192)

                if not second_response:
                    connection_closed = True

            except (BrokenPipeError, ConnectionResetError, OSError):
                connection_closed = True

    finally:
        sock.close()

    return (
        response.decode("iso-8859-1", errors="replace"),
        second_response.decode("iso-8859-1", errors="replace"),
        connection_closed,
    )

def extract_status(response):
    first_line = response.splitlines()[0] if response.splitlines() else ""
    parts = first_line.split()
    if len(parts) >= 2 and parts[0].startswith("HTTP/"):
        return parts[1]
    return "NO_STATUS"

def extract_body(response):
    if "\r\n\r\n" in response:
        return response.split("\r\n\r\n", 1)[1]
    if "\n\n" in response:
        return response.split("\n\n", 1)[1]
    return ""

def parse_backend_json(response):
    body = extract_body(response).strip()

    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return None

def classify(test, status, backend_json, connection_closed):
    expected_statuses = test.get("expected_statuses", [])
    should_reach_backend = test.get("should_reach_backend")
    expect_connection_close = test.get("expect_connection_close", False)

    reached_backend = backend_json is not None

    if should_reach_backend is False and reached_backend:
        return "Potential Non-Compliance: Reached Backend"

    if expected_statuses and status not in expected_statuses:
        return "Unexpected Status"

    if should_reach_backend is False and reached_backend:
        return "Potential Non-Compliance: Reached Backend"

    if should_reach_backend is True and not reached_backend:
        return "Unexpected: Did Not Reach Backend"

    if expect_connection_close and not connection_closed:
        return "Potential Non-Compliance: Connection Reused"

    return "Expected / Review"

def main():
    output_file = f"results/automated-results-detailed-{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv"

    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "RequirementID",
            "TestName",
            "Implementation",
            "StatusCode",
            "ReachedBackend",
            "BackendMethod",
            "BackendPath",
            "BackendHeaders",
            "BackendBody",
            "ConnectionClosed",
            "Classification",
            "FirstResponse",
            "SecondResponse",
        ])

        for test in TESTS:
            for implementation, (host, port) in TARGETS.items():
                try:
                    response, second_response, connection_closed = send_raw(
                    host,
                    port,
                    test["request"],
                    check_reuse=test.get("expect_connection_close", False),
                    incomplete_body_test=test.get("incomplete_body_test", False),
                )
                except Exception as e:
                    response = f"CLIENT_ERROR: {e}"
                    second_response = ""
                    connection_closed = False

                status = extract_status(response)
                backend_json = parse_backend_json(response)

                reached_backend = backend_json is not None
                backend_method = backend_json.get("method", "") if backend_json else ""
                backend_path = backend_json.get("path", "") if backend_json else ""
                backend_headers = json.dumps(backend_json.get("headers", {})) if backend_json else ""
                backend_body = backend_json.get("body", "") if backend_json else ""

                classification = classify(test, status, backend_json, connection_closed)

                writer.writerow([
                    test["id"],
                    test["name"],
                    implementation,
                    status,
                    reached_backend,
                    backend_method,
                    backend_path,
                    backend_headers,
                    backend_body,
                    connection_closed,
                    classification,
                    response.replace("\n", "\\n"),
                    second_response.replace("\n", "\\n"),
                ])

                print(
                    f"{test['id']} | {test['name']} | {implementation} | "
                    f"status={status} | backend={reached_backend} | {classification}"
                )

    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
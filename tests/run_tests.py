import socket
import csv
import json
from datetime import datetime

TARGETS = {
    "nginx": ("localhost", 8081),
    "haproxy": ("localhost", 8082),
}

TESTS = [

    # RQ-001
    {
        "id": "RQ-001",
        "name": "Invalid Content-Length",
        "request": (
            "POST /test HTTP/1.1\r\n"
            "Host: localhost\r\n"
            "Content-Length: abc\r\n"
            "\r\n"
            "HELLO"
        ),
        "expected_statuses": ["400"],
        "should_reach_backend": False,
    },

    # RQ-002
    {
        "id": "RQ-002",
        "name": "Bare CR Handling",
        "request": (
            "GET /test HTTP/1.1\r\n"
            "Host: localhost\r"
            "X-Test: value\r\n"
            "\r\n"
        ),
        "expected_statuses": ["200", "400"],
        "review_level": "manual_review",
    },

    # RQ-003
    {
        "id": "RQ-003",
        "name": "Whitespace Before First Header",
        "request": (
            "GET /test HTTP/1.1\r\n"
            " Host: localhost\r\n"
            "\r\n"
        ),
        "expected_statuses": ["200", "400"],
        "review_level": "manual_review",
    },

    # RQ-004
    {
        "id": "RQ-004",
        "name": "Incomplete Content-Length Body",
        "request": (
            "POST /test HTTP/1.1\r\n"
            "Host: localhost\r\n"
            "Content-Length: 100\r\n"
            "\r\n"
            "HELLO"
        ),
        "incomplete_body_test": True,
        "expected_statuses": ["NO_STATUS", "400", "408"],
        "should_reach_backend": False,
        "expect_connection_close": True,
    },
    
    # RQ-005
    {
        "id": "RQ-005",
        "name": "Chunked Transfer Coding Support",
        "request": (
            "POST /test HTTP/1.1\r\n"
            "Host: localhost\r\n"
            "Transfer-Encoding: chunked\r\n"
            "\r\n"
            "5\r\n"
            "HELLO\r\n"
            "0\r\n"
            "\r\n"
        ),
        "expected_statuses": ["200"],
        "should_reach_backend": True,
    },

    # RQ-006
    {
        "id": "RQ-006",
        "name": "Large Chunk Size Handling",
        "request": (
            "POST /test HTTP/1.1\r\n"
            "Host: localhost\r\n"
            "Transfer-Encoding: chunked\r\n"
            "\r\n"
            "FFFFFFFFFFFFFFFF\r\n"
        ),
        "review_level": "manual_review",
    },

    # RQ-007
    {
        "id": "RQ-007",
        "name": "Unknown Chunk Extensions",
        "request": (
            "POST /test HTTP/1.1\r\n"
            "Host: localhost\r\n"
            "Transfer-Encoding: chunked\r\n"
            "\r\n"
            "5;random=value\r\n"
            "HELLO\r\n"
            "0\r\n"
            "\r\n"
        ),
        "expected_statuses": ["200"],
        "should_reach_backend": True,
    },

    # RQ-008
    {
        "id": "RQ-008",
        "name": "Invalid HTTP Message Grammar",
        "request": (
            "INVALID_REQUEST\r\n"
            "\r\n"
        ),
        "expected_statuses": ["400"],
        "review_level": "manual_review",
    },

    # RQ-009
    {
        "id": "RQ-009",
        "name": "Missing Host Header",
        "request": (
            "GET /test HTTP/1.1\r\n"
            "X-Test-Case: RQ-009-MISSING-HOST\r\n"
            "Connection: close\r\n"
            "\r\n"
        ),
        "expected_statuses": ["400"],
        "should_reach_backend": False,
    },


    # RQ-010
    {
        "id": "RQ-010",
        "name": "obs-fold",
        "request": (
            "GET /test HTTP/1.1\r\n"
            "Host: localhost\r\n"
            "X-Test: value\r\n"
            "\tcontinued\r\n"
            "\r\n"
        ),
        "expected_statuses": ["200", "400"],
        "review_level": "manual_review",
    },

    # RQ-011
    {
        "id": "RQ-011",
        "name": "Unknown Transfer-Encoding",
        "request": (
            "POST /test HTTP/1.1\r\n"
            "Host: localhost\r\n"
            "Transfer-Encoding: unknown\r\n"
            "\r\n"
            "HELLO"
        ),
        "expected_statuses": ["400", "501"],
        "should_reach_backend": False,
    },

    # RQ-012
    {
        "id": "RQ-012",
        "name": "Content-Length and Transfer-Encoding Conflict",
        "request": (
            "POST /test HTTP/1.1\r\n"
            "Host: localhost\r\n"
            "Content-Length: 5\r\n"
            "Transfer-Encoding: chunked\r\n"
            "\r\n"
            "0\r\n"
            "\r\n"
            "HELLO"
        ),
        "expected_statuses": ["200", "400"],
        "expect_connection_close": True,
    },

    # RQ-013
    {
        "id": "RQ-013",
        "name": "Transfer-Encoding in HTTP/1.0",
        "request": (
            "POST /test HTTP/1.0\r\n"
            "Host: localhost\r\n"
            "Transfer-Encoding: chunked\r\n"
            "\r\n"
            "0\r\n"
            "\r\n"
        ),
        "expect_connection_close": True,
        "review_level": "manual_review",
    },

    # RQ-014
    {
        "id": "RQ-014",
        "name": "Transfer-Encoding Not Ending In Chunked",
        "request": (
            "POST /test HTTP/1.1\r\n"
            "Host: localhost\r\n"
            "Transfer-Encoding: chunked, gzip\r\n"
            "\r\n"
            "HELLO"
        ),
        "expected_statuses": ["400"],
        "expect_connection_close": True,
    },

    # RQ-015
    {
        "id": "RQ-015",
        "name": "Connection Close Semantics",
        "request": (
            "GET /test HTTP/1.1\r\n"
            "Host: localhost\r\n"
            "Connection: close\r\n"
            "\r\n"
        ),
        "expected_statuses": ["200"],
        "expect_connection_close": True,
    },

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
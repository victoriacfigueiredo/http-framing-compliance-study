from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class EchoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.respond()

    def do_POST(self):
        self.respond()

    def respond(self):
        content_length = int(self.headers.get("Content-Length", 0))

        data = {
            "method": self.command,
            "path": self.path,
            "request_version": self.request_version,
            "headers": dict(self.headers),
            "body": "",
            "body_read_error": None,
        }

        print("\n=== REQUEST HEADERS RECEIVED BY BACKEND ===", flush=True)
        print(json.dumps(data, indent=2), flush=True)

        try:
            body = self.rfile.read(content_length) if content_length else b""
            data["body"] = body.decode("utf-8", errors="replace")
        except Exception as e:
            data["body_read_error"] = repr(e)

        print("\n=== REQUEST FINAL BACKEND STATE ===", flush=True)
        print(json.dumps(data, indent=2), flush=True)
        print("===================================\n", flush=True)

        response = json.dumps(data).encode()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8080), EchoHandler)
    print("Backend listening on port 8080")
    server.serve_forever()
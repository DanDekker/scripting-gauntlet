"""Mock service for 055-localport-scan.

The harness binds it to a free port inside the drill's declared range and records the
chosen port in $WORK/mock.port so the grader knows which port the scan had to find.
"""

import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *args):
        pass

    def do_GET(self):
        body = b"up\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    port = int(os.environ.get("PORT", "0"))
    work = os.environ.get("WORK", "")
    if work:
        with open(os.path.join(work, "mock.port"), "w", encoding="utf-8") as fh:
            fh.write(f"{port}\n")
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()

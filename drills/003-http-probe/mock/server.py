"""Mock service for 003-http-probe. Binds 127.0.0.1:$PORT and serves a paginated API."""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

ITEMS = [{"id": i, "name": f"item-{i:02d}"} for i in range(1, 13)]
PAGE_SIZE = 5
VERSION = "2.3.1"


def page_of(number: int) -> dict:
    start = (number - 1) * PAGE_SIZE
    chunk = ITEMS[start : start + PAGE_SIZE]
    has_more = start + PAGE_SIZE < len(ITEMS)
    return {
        "items": chunk,
        "next": f"/api/v1/items?page={number + 1}" if has_more else None,
    }


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *args):  # keep the harness stderr clean
        pass

    def _send(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._send(200, {"ok": True, "version": VERSION})
            return
        if parsed.path == "/api/v1/items":
            raw = parse_qs(parsed.query).get("page", ["1"])[0]
            try:
                number = int(raw)
            except ValueError:
                self._send(400, {"error": "page must be an integer"})
                return
            if number < 1:
                self._send(400, {"error": "page must be >= 1"})
                return
            self._send(200, page_of(number))
            return
        self._send(404, {"error": "not found"})


def main() -> None:
    port = int(os.environ.get("PORT", "0"))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()

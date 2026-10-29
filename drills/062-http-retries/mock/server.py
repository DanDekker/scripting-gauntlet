"""Tiny deterministic server for the HTTP retry drill."""

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

HITS = Path(os.environ["WORK"]) / "hits.log"
counts = {}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        name = self.path.lstrip("/")
        counts[name] = counts.get(name, 0) + 1
        with HITS.open("a", encoding="utf-8") as log:
            log.write(name + "\n")

        if name == "steady":
            code, body = 200, {"items": ["a", "b"]}
        elif name == "flaky" and counts[name] < 3:
            code, body = 503, {"error": "warming up"}
        elif name == "flaky":
            code, body = 200, {"items": ["x", "y", "z"]}
        else:
            code, body = 404, {"error": "not found"}

        payload = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *_args):
        pass


HTTPServer(("127.0.0.1", int(os.environ["PORT"])), Handler).serve_forever()

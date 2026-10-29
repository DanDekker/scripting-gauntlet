"""Tiny deterministic paginated collection for the pagination drill."""

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

LOG = Path(os.environ["WORK"]) / "requests.log"

PAGES = {
    "": {
        "items": [
            {"id": 3, "name": "gamma"},
            {"id": 1, "name": "alpha"},
            {"id": 2, "name": "beta"},
        ],
        "next": "p2",
    },
    "p2": {
        "items": [
            {"id": 2, "name": "BETA-DUP"},
            {"id": 5, "name": "epsilon"},
        ],
        "next": "p3",
    },
    "p3": {"items": [{"id": 4, "name": "delta"}], "next": None},
}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        with LOG.open("a", encoding="utf-8") as log:
            log.write(self.path + "\n")

        if parsed.path != "/items":
            code, body = 404, {"error": "not found"}
        else:
            cursor = parse_qs(parsed.query).get("cursor", [""])[0]
            if cursor in PAGES:
                code, body = 200, PAGES[cursor]
            else:
                code, body = 400, {"error": f"unknown cursor: {cursor}"}

        payload = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *_args):
        pass


HTTPServer(("127.0.0.1", int(os.environ["PORT"])), Handler).serve_forever()

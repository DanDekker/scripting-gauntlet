#!/usr/bin/env python3
"""A small child process that publishes readiness and waits for a stop marker."""

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import sys
import time
from pathlib import Path

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        code, body = (200, b"ready\n") if self.path == "/health" else (404, b"missing\n")
        self.send_response(code)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args):
        pass


ready = Path(sys.argv[1])
stop = Path(sys.argv[2])
heartbeat = Path(sys.argv[3])
server = HTTPServer(("127.0.0.1", 0), Handler)
server.timeout = 0.025
heartbeat.write_text("0\n")
temporary = ready.with_suffix(".tmp")
temporary.write_text(json.dumps({"pid": os.getpid(), "port": server.server_port}) + "\n")
temporary.replace(ready)

count = 0
deadline = time.monotonic() + 12
while not stop.exists() and time.monotonic() < deadline:
    count += 1
    heartbeat.write_text(str(count) + "\n")
    server.handle_request()
server.server_close()

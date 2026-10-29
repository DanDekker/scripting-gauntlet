"""Probe the listener the solution started and record what it answered.

Runs after the solution exits, so this is an independent check: the solution cannot
fake it by writing a file itself. Always exits 0 — the verdict lives in probe.json so
the grader can explain what went wrong.
"""

import json
import os
import socket
import time
from pathlib import Path

port = int(os.environ["PORT"])
out = Path(os.environ["OUT"])

result = {"status": 0, "body": "", "error": ""}
deadline = time.monotonic() + 8

while time.monotonic() < deadline:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=2) as sock:
            sock.sendall(b"GET /health HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
            chunks = []
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                chunks.append(data)
        raw = b"".join(chunks).decode("utf-8", "replace")
        head, _, body = raw.partition("\r\n\r\n")
        if not body:
            head, _, body = raw.partition("\n\n")
        parts = head.split()
        status = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        result = {"status": status, "body": body}
        break
    except OSError as exc:
        result = {"status": 0, "body": "", "error": f"{type(exc).__name__}: {exc}"}
        time.sleep(0.25)

(out / "probe.json").write_text(json.dumps(result) + "\n", encoding="utf-8")

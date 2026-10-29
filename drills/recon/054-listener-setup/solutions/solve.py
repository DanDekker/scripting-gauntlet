#!/usr/bin/env python3
"""054-listener-setup — start a loopback responder, record its pid, let it outlive us."""

import os
import subprocess
import sys
from pathlib import Path

port = int(os.environ["PORT"])
out = Path(os.environ["OUT"])
work = Path(os.environ["WORK"])
out.mkdir(parents=True, exist_ok=True)

responder = work / "responder.py"
responder.write_text(
    """
import socket
import sys

RESPONSE = (
    b"HTTP/1.1 200 OK\\r\\n"
    b"Content-Type: text/plain\\r\\n"
    b"Content-Length: 13\\r\\n"
    b"\\r\\n"
    b"hello scriptdeck"
)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("127.0.0.1", int(sys.argv[1])))
server.listen(16)

while True:
    conn, _ = server.accept()
    try:
        conn.recv(4096)
        conn.sendall(RESPONSE)
    finally:
        conn.close()
""",
    encoding="utf-8",
)

# The child must not inherit our stdout, or the pipe stays open and the caller hangs.
log = (out / "listener.log").open("w", encoding="utf-8")
child = subprocess.Popen([sys.executable, str(responder), str(port)], stdout=log, stderr=log)

(out / "listener.pid").write_text(f"{child.pid}\n", encoding="utf-8")

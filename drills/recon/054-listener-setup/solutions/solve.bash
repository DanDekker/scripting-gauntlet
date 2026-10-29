#!/usr/bin/env bash
# 054-listener-setup — start the responder, record its pid, keep its fds off stdout.
set -euo pipefail

port="${PORT:?PORT not set}"
outdir="${OUT:?OUT not set}"
workdir="${WORK:?WORK not set}"
mkdir -p "$outdir"

cat > "$workdir/responder.py" <<'PY'
import socket
import sys

RESPONSE = (
    b"HTTP/1.1 200 OK\r\n"
    b"Content-Type: text/plain\r\n"
    b"Content-Length: 13\r\n"
    b"\r\n"
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
PY

# stdout/stderr go to the log: a backgrounded child holding our stdout keeps the
# pipe open and wedges whoever launched us.
python3 "$workdir/responder.py" "$port" > "$outdir/listener.log" 2>&1 &
echo $! > "$outdir/listener.pid"

#!/usr/bin/env python3
"""055-localport-scan — connect, and treat refusal as the normal answer."""

import json
import os
import socket
from pathlib import Path

out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

LOW, HIGH = 46000, 46010

open_ports = []
scanned = 0

for port in range(LOW, HIGH + 1):
    scanned += 1
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    try:
        sock.connect(("127.0.0.1", port))
    except OSError:
        continue  # refused or unreachable: the port is closed
    else:
        open_ports.append(port)
    finally:
        sock.close()

with (out / "open_ports.csv").open("w", newline="", encoding="utf-8") as fh:
    fh.write("port\n")
    for port in sorted(open_ports):
        fh.write(f"{port}\n")

summary = {"scanned": scanned, "open": len(open_ports)}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")

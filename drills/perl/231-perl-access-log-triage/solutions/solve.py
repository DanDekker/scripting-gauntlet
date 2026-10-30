#!/usr/bin/env python3
"""231-perl-access-log-triage — python twin."""

import json
import os
import re
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

pattern = re.compile(
    r'^(\S+)\s+\S+\s+\S+\s+\[[^\]]+\]\s+"[A-Z]+\s+\S+\s+HTTP/[0-9.]+"\s+(\d{3})\s+(\S+)'
)

ip_reqs = {}
ip_bytes = {}
status_counts = {"s2xx": 0, "s3xx": 0, "s4xx": 0, "s5xx": 0}
total_requests = 0
total_bytes = 0

for line in (IN / "access.log").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    m = pattern.match(line)
    if not m:
        continue
    ip, status_str, bytes_str = m.group(1), m.group(2), m.group(3)
    status = int(status_str)
    bytes_val = 0 if bytes_str == "-" else int(bytes_str)

    family = f"s{status // 100}xx"
    if family in status_counts:
        status_counts[family] += 1

    ip_reqs[ip] = ip_reqs.get(ip, 0) + 1
    ip_bytes[ip] = ip_bytes.get(ip, 0) + bytes_val

    total_requests += 1
    total_bytes += bytes_val

sorted_ips = sorted(
    ip_reqs.keys(),
    key=lambda x: (-ip_reqs[x], -ip_bytes[x], x),
)

with (OUT / "clients.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("ip,requests,bytes\n")
    for ip in sorted_ips:
        fh.write(f"{ip},{ip_reqs[ip]},{ip_bytes[ip]}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "requests": total_requests,
            "total_bytes": total_bytes,
            "s2xx": status_counts["s2xx"],
            "s3xx": status_counts["s3xx"],
            "s4xx": status_counts["s4xx"],
            "s5xx": status_counts["s5xx"],
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)

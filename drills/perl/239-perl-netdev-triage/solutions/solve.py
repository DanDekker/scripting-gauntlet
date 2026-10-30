#!/usr/bin/env python3
import json
from pathlib import Path

in_path = Path("in/net_dev.txt")
lines = in_path.read_text(encoding="utf-8").splitlines()

interfaces = []
healthy_count = 0
degraded_count = 0
down_count = 0
total_traffic = 0

for line in lines:
    line = line.strip()
    if ":" not in line:
        continue
    iface, data = line.split(":", 1)
    iface = iface.strip()
    cols = data.split()
    if len(cols) < 16:
        continue

    rx_bytes = int(cols[0])
    rx_packets = int(cols[1])
    rx_errs = int(cols[2])
    rx_drop = int(cols[3])

    tx_bytes = int(cols[8])
    tx_packets = int(cols[9])
    tx_errs = int(cols[10])
    tx_drop = int(cols[11])

    total_bytes = rx_bytes + tx_bytes
    total_packets = rx_packets + tx_packets
    total_errors = rx_errs + tx_errs
    total_drops = rx_drop + tx_drop

    if total_bytes == 0:
        status = "DOWN"
        down_count += 1
    elif total_errors > 0 or total_drops > 0:
        status = "DEGRADED"
        degraded_count += 1
    else:
        status = "HEALTHY"
        healthy_count += 1

    total_traffic += total_bytes

    interfaces.append({
        "interface": iface,
        "status": status,
        "total_bytes": total_bytes,
        "total_packets": total_packets,
        "total_errors": total_errors,
        "total_drops": total_drops,
    })

interfaces.sort(key=lambda x: (-x["total_bytes"], x["interface"]))

out_dir = Path("out")
out_dir.mkdir(parents=True, exist_ok=True)

tsv_lines = ["interface\tstatus\ttotal_bytes\ttotal_packets\ttotal_errors\ttotal_drops"]
for it in interfaces:
    tsv_lines.append(f"{it['interface']}\t{it['status']}\t{it['total_bytes']}\t{it['total_packets']}\t{it['total_errors']}\t{it['total_drops']}")
Path("out/interfaces.tsv").write_text("\n".join(tsv_lines) + "\n", encoding="utf-8")

top_iface = interfaces[0]["interface"] if interfaces else ""

summary = {
    "degraded_count": degraded_count,
    "down_count": down_count,
    "healthy_count": healthy_count,
    "top_interface": top_iface,
    "total_interfaces": len(interfaces),
    "total_traffic_bytes": total_traffic,
}

Path("out/summary.json").write_text(json.dumps(summary, separators=(",", ":")), encoding="utf-8")

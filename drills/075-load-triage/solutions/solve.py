#!/usr/bin/env python3
"""075-load-triage - averages first, then one precedence-ordered verdict."""

import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

rows = []
for host_dir in sorted((inp / "hosts").iterdir()):
    if not host_dir.is_dir():
        continue
    host = host_dir.name
    try:
        nproc = int((host_dir / "nproc").read_text().strip())
        load1 = float((host_dir / "loadavg").read_text().split()[0])
        samples = []
        for line in (host_dir / "vmstat").read_text().splitlines():
            fields = line.split()
            if len(fields) >= 17 and fields[0].isdigit():
                samples.append([float(value) for value in fields])
    except (OSError, ValueError, IndexError) as exc:
        raise SystemExit(f"{host}: cannot read capture: {exc}")
    if nproc <= 0:
        raise SystemExit(f"{host}: bad nproc")
    if not samples:
        raise SystemExit(f"{host}: no vmstat samples")

    count = len(samples)
    r_avg = sum(sample[0] for sample in samples) / count
    wa_avg = sum(sample[15] for sample in samples) / count
    busy = sum(sample[12] + sample[13] for sample in samples) / count
    swapped = any(sample[6] + sample[7] > 0 for sample in samples)

    if swapped:
        verdict = "memory"
    elif wa_avg >= 10:
        verdict = "io"
    elif r_avg >= 2 * nproc and busy >= 80:
        verdict = "cpu"
    else:
        verdict = "healthy"
    rows.append((host, verdict, load1 / nproc, r_avg, wa_avg, busy))

with (out / "triage.csv").open("w", newline="", encoding="utf-8") as fh:
    fh.write("host,verdict,load1_per_cpu,r_avg,wa_avg,busy_pct\n")
    for host, verdict, per_cpu, r_avg, wa_avg, busy in sorted(rows):
        fh.write(f"{host},{verdict},{per_cpu:.2f},{r_avg:.1f},{wa_avg:.1f},{busy:.1f}\n")

summary = {
    "hosts": len(rows),
    "saturated": sum(1 for row in rows if row[1] != "healthy"),
}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")

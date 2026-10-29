#!/usr/bin/env python3
"""131-port-scan-triage - scan log + approved-services sheet -> ports.csv + summary.json."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

STATES = {"open", "closed", "filtered"}
PORT = re.compile(r"[0-9]+")
RANGE = re.compile(r"([0-9]+)-([0-9]+)")
ATTENTION = {"wrong-service", "unexpected", "should-be-closed"}

Records = dict[tuple[int, str], tuple[str, str]]
Baseline = dict[int, tuple[str, str]]


def read_baseline(path: Path) -> Baseline:
    """port -> (service, expected), header and blank lines dropped."""
    baseline: Baseline = {}
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        cells = [cell.strip() for cell in line.split(",")]
        if cells[0].lower() == "port":
            continue
        if len(cells) != 3 or not PORT.fullmatch(cells[0]):
            raise SystemExit(f"{path}:{number}: expected port,service,expected: {raw!r}")
        baseline[int(cells[0])] = (cells[1], cells[2].lower())
    return baseline


def scan(path: Path) -> tuple[Records, int, int, int]:
    """Read the scan log into (port, proto) -> (state, service), last probe winning."""
    records: Records = {}
    lines = skipped = superseded = 0
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        lines += 1
        fields = raw.split()
        if len(fields) < 2:
            skipped += 1
            continue
        state = fields[1].lower()
        port_field = fields[0]
        if state not in STATES or "/" not in port_field:
            skipped += 1
            continue
        port_part, _, proto = port_field.partition("/")
        span = RANGE.fullmatch(port_part)
        if PORT.fullmatch(port_part):
            ports = [int(port_part)]
        elif span is not None:
            ports = list(range(int(span.group(1)), int(span.group(2)) + 1))
        else:
            skipped += 1
            continue
        service = fields[2] if len(fields) >= 3 else ""
        for port in ports:
            key = (port, proto)
            if key in records:
                superseded += 1
            records[key] = (state, service)
    return records, lines, skipped, superseded


def judge(port: int, state: str, service: str, baseline: Baseline) -> str:
    approved = baseline.get(port)
    if approved is None:
        return "unbaselined"
    expected_service, expected = approved
    if expected == "yes":
        if state != "open":
            return "unexpected"
        return "ok" if service == expected_service else "wrong-service"
    if state == "open":
        return "should-be-closed"
    return "ok"


def main() -> int:
    inp = Path(os.environ.get("IN", "in"))
    out = Path(os.environ.get("OUT", "out"))
    for name in ("scan.txt", "baseline.csv"):
        if not (inp / name).is_file():
            print(f"missing {inp / name}", file=sys.stderr)
            return 1

    baseline = read_baseline(inp / "baseline.csv")
    records, lines, skipped, superseded = scan(inp / "scan.txt")

    rows: list[tuple[int, str, str, str, str]] = []
    opened = unbaselined = attention = 0
    for (port, proto), (state, service) in records.items():
        verdict = judge(port, state, service, baseline)
        rows.append((port, proto, state, service, verdict))
        opened += state == "open"
        unbaselined += verdict == "unbaselined"
        attention += verdict in ATTENTION
    rows.sort(key=lambda row: (row[0], row[1]))

    out.mkdir(parents=True, exist_ok=True)
    body = ["port,proto,state,service,verdict"]
    body += [f"{port},{proto},{state},{service},{verdict}" for port, proto, state, service, verdict in rows]
    (out / "ports.csv").write_text("\n".join(body) + "\n", encoding="utf-8")

    summary = (
        "{"
        f'"lines":{lines},'
        f'"ports":{len(rows)},'
        f'"skipped":{skipped},'
        f'"superseded":{superseded},'
        f'"open":{opened},'
        f'"unbaselined":{unbaselined},'
        f'"attention":{attention}'
        "}\n"
    )
    (out / "summary.json").write_text(summary, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())

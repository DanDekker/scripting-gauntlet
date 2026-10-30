"""Grader for 239-perl-netdev-triage. Return [] on success, or a list of human-readable failures."""

import json


def verify(io):
    failures = []

    tsv_file = io.out / "interfaces.tsv"
    if not tsv_file.is_file():
        return ["missing out/interfaces.tsv"]

    expected_rows = [
        ["interface", "status", "total_bytes", "total_packets", "total_errors", "total_drops"],
        ["eth0", "DEGRADED", "78643200", "120000", "130", "17"],
        ["lo", "HEALTHY", "20971520", "40000", "0", "0"],
        ["wlan0", "HEALTHY", "20971520", "35000", "0", "0"],
        ["docker0", "DEGRADED", "3145728", "4500", "5", "0"],
        ["eth1", "DOWN", "0", "0", "0", "0"],
    ]

    lines = [line for line in tsv_file.read_text(encoding="utf-8").splitlines() if line]
    if len(lines) != len(expected_rows):
        failures.append(f"expected {len(expected_rows)} lines in out/interfaces.tsv, got {len(lines)}")
    else:
        for idx, (actual_line, exp) in enumerate(zip(lines, expected_rows)):
            parts = actual_line.split("\t")
            if parts != exp:
                failures.append(f"row {idx}: expected {exp!r}, got {parts!r}")

    summary_file = io.out / "summary.json"
    if not summary_file.is_file():
        failures.append("missing out/summary.json")
    else:
        try:
            data = json.loads(summary_file.read_text(encoding="utf-8"))
            if data.get("total_interfaces") != 5:
                failures.append(f"expected total_interfaces=5, got {data.get('total_interfaces')}")
            if data.get("healthy_count") != 2:
                failures.append(f"expected healthy_count=2, got {data.get('healthy_count')}")
            if data.get("degraded_count") != 2:
                failures.append(f"expected degraded_count=2, got {data.get('degraded_count')}")
            if data.get("down_count") != 1:
                failures.append(f"expected down_count=1, got {data.get('down_count')}")
            if data.get("total_traffic_bytes") != 123731968:
                failures.append(f"expected total_traffic_bytes=123731968, got {data.get('total_traffic_bytes')}")
            if data.get("top_interface") != "eth0":
                failures.append(f"expected top_interface='eth0', got {data.get('top_interface')!r}")
        except Exception as e:
            failures.append(f"invalid JSON in out/summary.json: {e}")

    return failures


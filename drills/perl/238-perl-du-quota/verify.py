"""Grader for 238-perl-du-quota. Return [] on success, or a list of human-readable failures."""

import json


def verify(io):
    failures = []

    alerts_file = io.out / "alerts.tsv"
    if not alerts_file.is_file():
        return ["missing out/alerts.tsv"]

    expected_rows = [
        ["path", "usage_bytes", "quota_bytes", "overage_bytes", "pct_used"],
        ["/home/bob", "1610612736", "1073741824", "536870912", "150.0"],
        ["/home/eve", "2684354560", "2147483648", "536870912", "125.0"],
        ["/home/frank", "838860800", "524288000", "314572800", "160.0"],
    ]

    lines = [line for line in alerts_file.read_text(encoding="utf-8").splitlines() if line]
    if len(lines) != len(expected_rows):
        failures.append(f"expected {len(expected_rows)} lines in out/alerts.tsv, got {len(lines)}")
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
            if data.get("total_checked") != 7:
                failures.append(f"expected total_checked=7, got {data.get('total_checked')}")
            if data.get("over_quota_count") != 3:
                failures.append(f"expected over_quota_count=3, got {data.get('over_quota_count')}")
            if data.get("total_overage_bytes") != 1388314624:
                failures.append(f"expected total_overage_bytes=1388314624, got {data.get('total_overage_bytes')}")
            if data.get("top_offender") != "/home/bob":
                failures.append(f"expected top_offender='/home/bob', got {data.get('top_offender')!r}")
        except Exception as e:
            failures.append(f"invalid JSON in out/summary.json: {e}")

    return failures


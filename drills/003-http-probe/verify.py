"""Grader for 003-http-probe.

The mock server is deterministic: 12 items over 3 pages of 5/5/2.
"""

import json

EXPECTED_IDS = list(range(1, 13))
EXPECTED_REPORT = {"ok": True, "version": "2.3.1", "item_count": 12, "pages": 3}


def verify(io):
    failures = []

    items_path = io.out / "items.json"
    if not items_path.is_file():
        failures.append("missing out/items.json")
    else:
        try:
            items = json.loads(items_path.read_text(encoding="utf-8"))
        except Exception as exc:
            failures.append(f"items.json is not valid JSON: {exc}")
            items = None
        if items is not None:
            if not isinstance(items, list):
                failures.append(f"items.json: expected an array, got {type(items).__name__}")
            else:
                ids = [item.get("id") if isinstance(item, dict) else None for item in items]
                if ids != EXPECTED_IDS:
                    failures.append(
                        f"items.json: expected ids {EXPECTED_IDS[0]}..{EXPECTED_IDS[-1]} "
                        f"in ascending order, got {ids[:14]}"
                    )
                elif any(not isinstance(item.get("name"), str) for item in items):
                    failures.append("items.json: every item needs a string 'name'")

    report_path = io.out / "report.json"
    if not report_path.is_file():
        failures.append("missing out/report.json")
    else:
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except Exception as exc:
            failures.append(f"report.json is not valid JSON: {exc}")
        else:
            if not isinstance(report, dict):
                failures.append("report.json: expected an object")
            else:
                for key, want in EXPECTED_REPORT.items():
                    if key not in report:
                        failures.append(f"report.json: missing key {key!r}")
                    elif report[key] != want:
                        failures.append(f"report.json[{key!r}]: expected {want!r}, got {report[key]!r}")
                for key in report:
                    if key not in EXPECTED_REPORT:
                        failures.append(f"report.json: unexpected key {key!r}")

    return failures

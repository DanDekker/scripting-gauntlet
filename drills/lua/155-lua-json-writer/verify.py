"""Grader for 155-lua-json-writer.

The report is parsed as JSON and compared field by field, so the grader checks the
values rather than the bytes. Numeric types matter: an integral score must arrive as a
JSON integer, not as 3.0.
"""

import json
import math

EXPECTED_RECORDS = [
    {"id": 1, "name": "Widget", "score": 3, "note": "plain"},
    {"id": 2, "name": "Ada Lovelace", "score": 2.5, "note": 'has "quotes" and \\ backslash'},
    {"id": 3, "name": "Café", "score": 0.3, "note": "tab\tand bell\x07"},
    {"id": 4, "name": "Bad", "score": 1.5, "note": None},
]


def verify(io) -> list[str]:
    path = io.out / "report.json"
    if not path.is_file():
        return ["missing out/report.json"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"report.json is not valid JSON: {exc}"]

    if not isinstance(data, dict) or set(data) != {"records", "count", "invalid"}:
        return ["report.json must have exactly the keys records, count and invalid"]

    failures: list[str] = []
    if data["count"] != 4:
        failures.append(f"count: expected 4, got {data['count']!r}")
    if data["invalid"] != 1:
        failures.append(f"invalid: expected 1, got {data['invalid']!r}")

    records = data["records"]
    if not isinstance(records, list):
        return failures + ["records must be an array"]
    if len(records) != len(EXPECTED_RECORDS):
        failures.append(f"records: expected {len(EXPECTED_RECORDS)} records, got {len(records)}")
        return failures

    for index, (got, want) in enumerate(zip(records, EXPECTED_RECORDS), start=1):
        if not isinstance(got, dict) or set(got) != set(want):
            failures.append(f"record {index}: expected the keys id, name, score and note")
            continue
        if type(got["id"]) is not int or got["id"] != want["id"]:
            failures.append(f"record {index}: id must be the integer {want['id']}, got {got['id']!r}")
        if got["name"] != want["name"]:
            failures.append(f"record {index}: name must be {want['name']!r}, got {got['name']!r}")
        if want["score"] == 3:
            if type(got["score"]) is not int or got["score"] != 3:
                failures.append(
                    f"record {index}: an integral score must be the integer 3, got {got['score']!r}"
                )
        elif not isinstance(got["score"], (int, float)) or not math.isclose(
            float(got["score"]), want["score"], abs_tol=1e-9
        ):
            failures.append(f"record {index}: score must be {want['score']!r}, got {got['score']!r}")
        if got["note"] != want["note"]:
            failures.append(f"record {index}: note must be {want['note']!r}, got {got['note']!r}")
    return failures

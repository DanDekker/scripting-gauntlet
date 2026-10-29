"""Grader for 142-function-call-repair."""

import json

import verifylib

EXPECTED_REPAIRED = [
    {"call_id": "c1", "name": "search", "status": "valid", "args": {"limit": 10, "query": "hello"}},
    {"call_id": "c2", "name": "read_file", "status": "repaired", "args": {"line": 3, "path": "foo.py"}},
    {"call_id": "c3", "name": "search", "status": "repaired", "args": {"a": 1}},
    {
        "call_id": "c4",
        "name": "cache_set",
        "status": "repaired",
        "args": {"cursor": None, "deep": True, "dry_run": False},
    },
    {"call_id": "c5", "name": "query", "status": "repaired", "args": {"num": 5, "query": "test"}},
    {"call_id": "c7", "name": "batch", "status": "valid", "args": [1, 2, 3]},
    {"call_id": "c10", "name": "lookup", "status": "repaired", "args": {"key": "value"}},
    {"call_id": "c11", "name": "toggle", "status": "repaired", "args": {"flag": True, "n": None}},
    {"call_id": "c12", "name": "padded", "status": "valid", "args": {"a": 1}},
    {"call_id": "c13", "name": "nested", "status": "repaired", "args": {"items": [1, 2]}},
]


def _check_jsonl(path):
    if not path.is_file():
        return ["missing repaired.jsonl"], []
    records = []
    failures = []
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            failures.append(f"repaired.jsonl line {index} is not JSON: {exc}")
    return failures, records


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "report.csv",
        ["call_id", "name", "status"],
        [
            ("c1", "search", "valid"),
            ("c2", "read_file", "repaired"),
            ("c3", "search", "repaired"),
            ("c4", "cache_set", "repaired"),
            ("c5", "query", "repaired"),
            ("c6", "flag", "unfixable"),
            ("c7", "batch", "valid"),
            ("c8", "broken", "unfixable"),
            ("c10", "lookup", "repaired"),
            ("c11", "toggle", "repaired"),
            ("c12", "padded", "valid"),
            ("c13", "nested", "repaired"),
        ],
    )

    jsonl_failures, records = _check_jsonl(io.out / "repaired.jsonl")
    failures += jsonl_failures
    if len(records) != len(EXPECTED_REPAIRED):
        failures.append(
            f"repaired.jsonl: expected {len(EXPECTED_REPAIRED)} records, got {len(records)}"
        )
    for index, (want, got) in enumerate(zip(EXPECTED_REPAIRED, records), start=1):
        if not isinstance(got, dict) or set(got) != {"call_id", "name", "status", "args"}:
            failures.append(f"repaired.jsonl record {index}: expected the 4 keys, got {got!r}")
            continue
        if got != want:
            failures.append(f"repaired.jsonl record {index}: expected {want!r}, got {got!r}")

    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "total_calls": 12,
            "valid_count": 3,
            "repaired_count": 7,
            "unfixable_count": 2,
        },
    )
    return failures

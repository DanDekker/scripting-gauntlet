"""Grader for 133-structured-extraction."""

import json

import verifylib

STATUS_ROWS = [
    ("r01", "extracted", "object"),
    ("r02", "extracted", "array"),
    ("r03", "extracted", "object"),
    ("r04", "extracted", "object"),
    ("r05", "failed", "none"),
    ("r06", "failed", "none"),
    ("r07", "failed", "none"),
    ("r08", "extracted", "array"),
    ("r09", "extracted", "object"),
    ("r10", "extracted", "object"),
    ("r11", "extracted", "object"),
    ("r12", "failed", "none"),
]

EXTRACTED = [
    {
        "id": "r01",
        "type": "object",
        "keys_or_length": 3,
        "data": {"tool": "search", "args": {"query": "weather in Oslo"}, "max_results": 5},
    },
    {"id": "r02", "type": "array", "keys_or_length": 3, "data": ["a1", "b2", "c3"]},
    {
        "id": "r03",
        "type": "object",
        "keys_or_length": 2,
        "data": {"retries": 3, "backoff": {"enabled": True, "base_ms": 250}},
    },
    {"id": "r04", "type": "object", "keys_or_length": 2, "data": {"status": "ok", "count": 7}},
    {"id": "r08", "type": "array", "keys_or_length": 2, "data": ["alpha", "beta"]},
    {"id": "r09", "type": "object", "keys_or_length": 2, "data": {"ok": True, "id": 42}},
    {
        "id": "r10",
        "type": "object",
        "keys_or_length": 3,
        "data": {
            "service": "api",
            "ports": [8080, 8443],
            "tls": {"enabled": True, "min_version": "1.2"},
        },
    },
    {"id": "r11", "type": "object", "keys_or_length": 1, "data": {"choice": "b"}},
]


def verify(io) -> list[str]:
    failures = verifylib.table(io.out / "status.csv", ["id", "status", "type"], STATUS_ROWS)
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "total_responses": 12,
            "extracted_count": 8,
            "failed_count": 4,
            "objects_count": 6,
            "arrays_count": 2,
        },
    )

    path = io.out / "extracted.jsonl"
    if not path.is_file():
        failures.append("missing extracted.jsonl")
        return failures

    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(lines) != len(EXTRACTED):
        failures.append(f"extracted.jsonl: expected {len(EXTRACTED)} lines, got {len(lines)}")

    for position, (line, want) in enumerate(zip(lines, EXTRACTED), start=1):
        try:
            got = json.loads(line)
        except json.JSONDecodeError as exc:
            failures.append(f"extracted.jsonl line {position}: not JSON ({exc})")
            continue
        if got != want:
            failures.append(f"extracted.jsonl line {position}: expected {want!r}, got {got!r}")
            continue
        if line != json.dumps(got, separators=(",", ":"), ensure_ascii=False):
            failures.append(
                f"extracted.jsonl line {position}: not compact single-line JSON: {line!r}"
            )
    return failures

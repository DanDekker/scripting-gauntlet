"""Grader for 035-split-merge.

23 data rows at 5 per chunk is 5 chunks: 5, 5, 5, 5, 3.
"""

import csv

import verifylib

HEADER = ["event_id", "actor", "action", "detail"]
SIZES = [5, 5, 5, 5, 3]
FIRST_ID = {1: "1001", 2: "1006", 3: "1011", 4: "1016", 5: "1021"}


def read_rows(path):
    with path.open(newline="", encoding="utf-8") as fh:
        return [row for row in csv.reader(fh) if any(cell.strip() for cell in row)]


def verify(io):
    failures = []
    source = io.inp / "events.csv"

    for index, size in enumerate(SIZES, start=1):
        chunk = io.out / f"chunk_{index:02d}.csv"
        if not chunk.is_file():
            failures.append(f"missing out/chunk_{index:02d}.csv")
            continue
        rows = read_rows(chunk)
        if not rows:
            failures.append(f"out/chunk_{index:02d}.csv is empty")
            continue
        if rows[0] != HEADER:
            failures.append(f"out/chunk_{index:02d}.csv header: expected {HEADER}, got {rows[0]}")
        body = rows[1:]
        if len(body) != size:
            failures.append(
                f"out/chunk_{index:02d}.csv: expected {size} data rows, got {len(body)}"
            )
        elif body and body[0][0] != FIRST_ID[index]:
            failures.append(
                f"out/chunk_{index:02d}.csv: first data row should be event {FIRST_ID[index]}, "
                f"got {body[0][0]!r}"
            )

    extra = sorted(p.name for p in io.out.glob("chunk_*.csv") if p.name not in {
        f"chunk_{i:02d}.csv" for i in range(1, len(SIZES) + 1)
    })
    if extra:
        failures.append(f"out/: unexpected chunk files {extra} (23 rows is 5 chunks)")

    merged = io.out / "merged.csv"
    if not merged.is_file():
        failures.append("missing out/merged.csv")
    else:
        want = source.read_bytes()
        got = merged.read_bytes()
        if got != want:
            failures.append(
                "out/merged.csv: reassembly is not byte-identical to in/events.csv "
                f"({len(got)} bytes vs {len(want)})"
            )

    failures += verifylib.json_eq(
        io.out / "report.json",
        {"rows": 23, "chunk_size": 5, "chunks": 5, "roundtrip": True},
    )
    return failures

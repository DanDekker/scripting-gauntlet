"""Grader for 066-benchmark-runner."""

import csv
import math
import statistics

import verifylib

EXPECTED_CHECKSUM = "1439918"
CASES = ["generator", "loop"]


def verify(io):
    failures = verifylib.json_eq(
        io.out / "summary.json",
        {"cases": 2, "warmups_per_case": 1, "samples_per_case": 5},
    )
    samples_path = io.out / "samples.csv"
    if not samples_path.is_file():
        failures.append("missing samples.csv")
        return failures
    try:
        with samples_path.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != ["case", "run", "seconds", "checksum"]:
                failures.append(f"samples.csv header is invalid: {reader.fieldnames}")
            rows = list(reader)
    except (OSError, csv.Error) as exc:
        return failures + [f"samples.csv cannot be parsed: {exc}"]
    if len(rows) != 10:
        failures.append(f"samples.csv: expected 10 rows, got {len(rows)}")
    keys = [(row.get("case"), row.get("run")) for row in rows]
    wanted = [(case, str(run)) for case in CASES for run in range(1, 6)]
    if keys != wanted:
        failures.append(f"samples.csv case/run order: expected {wanted}, got {keys}")
    timings = {case: [] for case in CASES}
    for row in rows:
        if row.get("checksum") != EXPECTED_CHECKSUM:
            failures.append(f"{row.get('case')} run {row.get('run')}: wrong checksum")
            break
        try:
            elapsed = float(row["seconds"])
            if elapsed <= 0:
                raise ValueError
            timings[row["case"]].append(elapsed)
        except (KeyError, ValueError):
            failures.append(f"{row.get('case')} run {row.get('run')}: invalid elapsed time")
            break

    summary_path = io.out / "summary.csv"
    if not summary_path.is_file():
        failures.append("missing summary.csv")
        return failures
    try:
        with summary_path.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != ["case", "samples", "median_seconds", "p95_seconds", "checksum"]:
                failures.append(f"summary.csv header is invalid: {reader.fieldnames}")
            summaries = list(reader)
    except (OSError, csv.Error) as exc:
        return failures + [f"summary.csv cannot be parsed: {exc}"]
    if [row.get("case") for row in summaries] != CASES:
        failures.append("summary.csv must have generator then loop")
    if len(summaries) == 2:
        for row in summaries:
            try:
                median = float(row["median_seconds"])
                p95 = float(row["p95_seconds"])
                ordered = sorted(timings[row["case"]])
                expected_median = statistics.median(ordered)
                expected_p95 = ordered[math.ceil(0.95 * len(ordered)) - 1]
                if (
                    int(row["samples"]) != 5
                    or abs(median - expected_median) > 0.0000011
                    or abs(p95 - expected_p95) > 0.0000011
                ):
                    raise ValueError
                if row["checksum"] != EXPECTED_CHECKSUM:
                    raise ValueError
            except (KeyError, ValueError):
                failures.append(f"summary.csv {row.get('case')}: invalid statistics")
                break
    return failures

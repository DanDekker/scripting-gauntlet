"""Grader for 210-perl-print-byte-count.

"alpha\\nbravo\\ncharlie\\ncafé\\n" is 26 bytes (café is 5 bytes in UTF-8);
print returns 1 per call, so a solution that sums the return value reports 4.
"""

import verifylib

EXPECTED_LINES = ["alpha", "bravo", "charlie", "café"]

EXPECTED_SUMMARY = {"items": 4, "bytes": 26}


def verify(io):
    failures = verifylib.lines(io.out / "report.txt", EXPECTED_LINES)

    report = io.out / "report.txt"
    if report.is_file():
        actual_bytes = len(report.read_bytes())
        if actual_bytes != EXPECTED_SUMMARY["bytes"]:
            failures.append(
                f"out/report.txt: expected {EXPECTED_SUMMARY['bytes']} bytes, got {actual_bytes}"
            )
    else:
        failures.append("missing report.txt")

    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures

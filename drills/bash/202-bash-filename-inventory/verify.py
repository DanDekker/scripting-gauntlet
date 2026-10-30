"""Grader for 202-bash-filename-inventory."""

import verifylib

EXPECTED = {
    "plain.txt": 6,
    "reports/My Report.txt": 10,
    "reports/annual summary.pdf": 16,
    "reports/notes.txt": 6,
    "weird name/deep file.dat": 5,
}

EXPECTED_SUMMARY = {"files": 5, "total_bytes": 43, "spaces": 3}


def verify(io):
    failures: list[str] = []
    path = io.out / "manifest.csv"
    if not path.is_file():
        failures.append("missing manifest.csv")
        return failures

    header, rows = verifylib.read_csv(path)
    if header != ["path", "bytes"]:
        failures.append(f"manifest.csv header: expected ['path', 'bytes'], got {header}")
        return failures

    got: dict[str, str] = {}
    for row in rows:
        if len(row) != 2:
            failures.append(f"manifest.csv: malformed row {row!r}")
            continue
        got[row[0]] = row[1]

    for expected_path, expected_bytes in EXPECTED.items():
        if expected_path not in got:
            failures.append(f"manifest.csv: missing path {expected_path!r}")
            continue
        try:
            actual = int(got[expected_path])
        except ValueError:
            failures.append(
                f"manifest.csv[{expected_path}]: expected {expected_bytes} bytes, got {got[expected_path]!r}"
            )
            continue
        if actual != expected_bytes:
            failures.append(
                f"manifest.csv[{expected_path}]: expected {expected_bytes} bytes, got {actual}"
            )

    for extra in sorted(got):
        if extra not in EXPECTED:
            failures.append(f"manifest.csv: unexpected path {extra!r}")

    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures

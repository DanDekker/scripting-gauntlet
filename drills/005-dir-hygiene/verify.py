"""Grader for 005-dir-hygiene.

Expected mapping is derived from the fixtures by the contract in PROMPT.md: junk dropped,
content-deduped (shortest path wins), normalized, sorted into <ext>/.
"""

import csv
import hashlib

# original (relative to in/messy) -> clean (relative to out/clean)
EXPECTED = {
    "deep/nested/data.csv": "csv/data.csv",
    "notes.txt": "txt/notes.txt",
    "old_report.pdf": "pdf/old_report.pdf",
    "photo1.jpg": "jpg/photo1.jpg",
    "readme.md": "md/readme.md",
}

HEADER = ["original", "clean", "sha256", "bytes"]


def verify(io):
    failures = []
    clean = io.out / "clean"
    messy = io.fixtures / "messy"

    if not clean.is_dir():
        return ["missing out/clean/"]

    actual = sorted(
        str(path.relative_to(clean)).replace("\\", "/")
        for path in clean.rglob("*")
        if path.is_file()
    )
    expected = sorted(EXPECTED.values())

    missing = [p for p in expected if p not in actual]
    extra = [p for p in actual if p not in expected]
    if missing:
        failures.append(f"out/clean/: missing {missing} (junk or duplicates survived?)")
    if extra:
        failures.append(f"out/clean/: unexpected {extra} (junk or duplicates survived?)")

    for original, cleaned in EXPECTED.items():
        source = messy / original
        target = clean / cleaned
        if target.is_file() and source.is_file():
            if target.read_bytes() != source.read_bytes():
                failures.append(f"out/clean/{cleaned}: content does not match {original}")

    manifest = io.out / "manifest.csv"
    if not manifest.is_file():
        failures.append("missing out/manifest.csv")
        return failures

    with manifest.open(newline="", encoding="utf-8") as fh:
        rows = [row for row in csv.reader(fh) if any(cell.strip() for cell in row)]

    if not rows:
        return failures + ["out/manifest.csv is empty"]

    if [cell.strip() for cell in rows[0]] != HEADER:
        return failures + [f"manifest.csv header: expected {HEADER}, got {rows[0]!r}"]

    data = rows[1:]
    if len(data) != len(EXPECTED):
        failures.append(f"manifest.csv: expected {len(EXPECTED)} rows, got {len(data)}")

    originals = [row[0].strip() for row in data if row]
    if originals != sorted(originals):
        failures.append("manifest.csv: rows must be sorted by original ascending")

    for row in data:
        if len(row) != 4:
            failures.append(f"manifest.csv: expected 4 columns, got {len(row)}: {row!r}")
            continue
        original, cleaned, digest, size = (cell.strip() for cell in row)
        if original not in EXPECTED:
            failures.append(f"manifest.csv: unexpected original {original!r} (junk or duplicate?)")
            continue
        if cleaned != EXPECTED[original]:
            failures.append(
                f"manifest.csv {original!r}: expected clean {EXPECTED[original]!r}, got {cleaned!r}"
            )
        source = messy / original
        if not source.is_file():
            failures.append(f"manifest.csv: {original!r} is not in the fixtures")
            continue
        payload = source.read_bytes()
        if digest.lower() != hashlib.sha256(payload).hexdigest():
            failures.append(f"manifest.csv {original!r}: sha256 does not match the content")
        if size != str(len(payload)):
            failures.append(f"manifest.csv {original!r}: expected {len(payload)} bytes, got {size!r}")

    return failures

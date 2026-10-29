"""Grader for 034-file-type-sniff.

Every expectation below is the contract from PROMPT.md applied by hand to setup.py's
output: kind from the signature table, magic from the first 8 bytes.
"""

import verifylib

ROWS = [
    ("annual.csv", "gzip", "1f8b080000000000"),
    ("backup.txt", "zip", "504b030414000000"),
    ("cache.bin", "unknown", "1337beef00002a9c"),
    ("chart.jpg", "jpeg", "ffd8ffe000104a46"),
    ("index.html", "elf", "7f454c4602010100"),
    ("notes.txt", "png", "89504e470d0a1a0a"),
    ("payload.dat", "utf16le", "fffe6b0065007900"),
    ("plain.txt", "ascii", "69642c6e616d652c"),
    ("readme.json", "pdf", "255044462d312e37"),
    ("vendor.csv", "utf8bom", "efbbbf69642c6e61"),
]


def verify(io):
    failures = verifylib.table(io.out / "types.csv", ["filename", "kind", "magic"], ROWS)
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"files": 10, "kinds": 10, "text_files": 3},
    )
    return failures

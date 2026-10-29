"""Generate the byte-level fixture for 155-lua-json-writer.

One note field carries a tab and a bell character, neither of which can be
committed as readable text.
"""

import os
from pathlib import Path

inp = Path(os.environ["IN"])
inp.mkdir(parents=True, exist_ok=True)

HEADER = b"id\tname\tscore\tnote\n"

ROWS = [
    b"1\tWidget\t3\tplain",
    b'2\tAda Lovelace\t2.5\thas "quotes" and \\ backslash',
    "3\tCafé\t0.30000000000000004\ttab\tand bell\x07".encode("utf-8"),
    b"4\tBad\t1.5\t",
    b"five\tWidget\t2\tplain",
]

(inp / "records.tsv").write_bytes(HEADER + b"\n".join(ROWS) + b"\n")

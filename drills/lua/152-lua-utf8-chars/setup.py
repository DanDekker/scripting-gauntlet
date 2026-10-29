"""Generate the byte-level fixture for 152-lua-utf8-chars.

The invalid line carries a raw 0xFF byte, which cannot be committed as text.
"""

import os
from pathlib import Path

inp = Path(os.environ["IN"])
inp.mkdir(parents=True, exist_ok=True)

LINES = [
    b"hello world",
    b"caf\xc3\xa9",
    b"\xe6\x97\xa5\xe6\x9c\xac\xe8\xaa\x9e",
    b"na\xc3\xafve",
    b"bad\xffbyte",
    b"emoji \xf0\x9f\x8e\x89 ok",
    b"truncate me please",
]

(inp / "mixed.txt").write_bytes(b"\n".join(LINES) + b"\n")

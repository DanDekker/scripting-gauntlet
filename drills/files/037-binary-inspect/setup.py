"""Build the binary blob for 037-binary-inspect.

The blob is deliberately byte-exact: NUL padding, an embedded PNG signature, a tab that
splits an otherwise printable run, and a string too short to count.
"""

import os
from pathlib import Path

inp = Path(os.environ["IN"])
inp.mkdir(parents=True, exist_ok=True)

PARTS = [
    b"\x00" * 3,  # leading padding
    b"scriptdeck blob v1",
    b"\x00" * 2,
    b"\x89PNG\r\n\x1a\n",  # the embedded file header
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x10",
    b"chunk-meta",
    b"\x00",
    b"\xde\xad\xbe\xef",
    b"vendor: acme corp",
    b"\x00" * 5,
    b"build\tdate=2026-10-29",  # a tab is not printable, so this run splits
    b"\x00" * 2,
    b"EOF",  # too short to be a string
    b"\x01\x02\xfe\xff",
    b"\x00",
]

(inp / "blob.bin").write_bytes(b"".join(PARTS))

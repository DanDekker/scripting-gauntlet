"""Generate the five encodings for 015-encodings.

These cannot be committed as text: the UTF-16 and latin-1 files are not valid UTF-8,
and a BOM is invisible in a diff.
"""

import os
from pathlib import Path

inp = Path(os.environ["IN"])
inp.mkdir(parents=True, exist_ok=True)

HEADER = "id,name,city\n"

FILES = {
    "utf8": (HEADER + "1,Zoë,Montréal\n", "utf-8", b""),
    "utf8bom": (HEADER + "2,Björn,Stockholm\n", "utf-8", b"\xef\xbb\xbf"),
    "utf16le": (HEADER + "3,Renée,Lyon\n", "utf-16-le", b"\xff\xfe"),
    "latin1": (HEADER + "4,Café,Montréal\n", "latin-1", b""),
    "crlf": (HEADER + "5,Ana,Lisboa\r\n", "utf-8", b""),
}

for name, (text, encoding, prefix) in FILES.items():
    (inp / f"{name}.csv").write_bytes(prefix + text.encode(encoding))

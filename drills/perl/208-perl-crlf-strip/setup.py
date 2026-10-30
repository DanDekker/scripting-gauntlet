#!/usr/bin/env python3
"""Build the CRLF fixture for 208-perl-crlf-strip.

Git will not carry a carriage return cleanly, so the file is generated with the
exact bytes the drill needs: CRLF line endings, no trailing newline.
"""

import os
from pathlib import Path

IN = Path(os.environ["IN"])

rows = [
    "sensor,label,value",
    "s1,room a,21.5",
    "s2,room b,19.0",
]
(IN / "measurements.csv").write_bytes(("\r\n".join(rows) + "\r\n").encode("utf-8"))

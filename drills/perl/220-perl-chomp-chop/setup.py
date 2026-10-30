#!/usr/bin/env python3
"""Build the fixture for 220-perl-chomp-chop.

The file must end WITHOUT a trailing newline, so the last line has no record
separator for chomp to remove.
"""

import os
from pathlib import Path

IN = Path(os.environ["IN"])

(IN / "notes.txt").write_bytes(b"alpha\nbravo\ngamma")

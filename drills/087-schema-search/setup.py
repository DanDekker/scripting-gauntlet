#!/usr/bin/env python3
"""Put a UTF-8 BOM in front of the quoted header, the way an export would."""

import os
from pathlib import Path

inp = Path(os.environ["IN"])
export = inp / "dump" / "d" / "export.csv"
text = export.read_text(encoding="utf-8")
header, _, rest = text.partition("\n")
quoted = ",".join(f'"{cell}"' for cell in header.split(","))
export.write_text("\ufeff" + quoted + "\n" + rest, encoding="utf-8")

"""Generate the compressed inputs for 016-archives."""

import gzip
import io
import os
import tarfile
from pathlib import Path

inp = Path(os.environ["IN"])
inp.mkdir(parents=True, exist_ok=True)

HEADER = "id,region,amount\n"

SALES = HEADER + "1,North,100\n2,South,50\n3,North,25\n"
OCTOBER = HEADER + "4,North,75\n5,South,200\n6,East,30\n"

with gzip.open(inp / "sales.csv.gz", "wb") as fh:
    fh.write(SALES.encode("utf-8"))

with tarfile.open(inp / "archive.tar.gz", "w:gz") as tar:
    for name, text in (
        ("oct/2026-10.csv", OCTOBER),
        ("README.txt", "monthly export\n"),
    ):
        payload = text.encode("utf-8")
        info = tarfile.TarInfo(name)
        info.size = len(payload)
        tar.addfile(info, io.BytesIO(payload))

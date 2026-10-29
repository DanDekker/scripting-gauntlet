"""Build the mislabelled inputs for 034-file-type-sniff.

Every extension here lies, and the payloads are binary or non-UTF-8, so they cannot be
committed as text.
"""

import gzip
import io
import os
import zipfile
from pathlib import Path

inp = Path(os.environ["IN"])
inp.mkdir(parents=True, exist_ok=True)

PNG = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00"
PDF = b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n%%EOF\n"
ELF = b"\x7fELF\x02\x01\x01\x00" + b"\x00" * 8 + b"\x03\x00>\x00" + b"\x40\x00\x00\x00"
JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00"
CSV = b"id,name,total\n1,ada,10\n2,grace,20\n"

(inp / "notes.txt").write_bytes(PNG + b"\x00" * 8)
(inp / "readme.json").write_bytes(PDF)
(inp / "index.html").write_bytes(ELF)
(inp / "chart.jpg").write_bytes(JPEG + b"\x00" * 8)
(inp / "annual.csv").write_bytes(gzip.compress(CSV, mtime=0))
(inp / "vendor.csv").write_bytes(b"\xef\xbb\xbf" + CSV)
(inp / "payload.dat").write_bytes(b"\xff\xfe" + "key\tvalue\n".encode("utf-16-le"))
(inp / "plain.txt").write_bytes(CSV)
(inp / "cache.bin").write_bytes(
    bytes([0x13, 0x37, 0xBE, 0xEF, 0x00, 0x00, 0x2A, 0x9C, 0xFE, 0x11])
)

archive = io.BytesIO()
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.writestr("export/2026-10.csv", CSV.decode())
(inp / "backup.txt").write_bytes(archive.getvalue())

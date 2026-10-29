#!/usr/bin/env python3
"""187-lua-binary-pack — python twin with identical contract."""

import json
import os
import struct
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

data = (IN / "stream.bin").read_bytes()
pos = 0
n = len(data)

frames = []
counts = {
    "valid": 0,
    "corrupt_checksum": 0,
    "bad_magic": 0,
    "truncated": 0,
}

while pos < n:
    if pos + 6 > n:
        counts["truncated"] += 1
        frames.append((0, "truncated", 0, ""))
        break

    magic, msg_id = struct.unpack_from(">HI", data, pos)
    # Check payload length
    if pos + 8 > n:
        counts["truncated"] += 1
        frames.append((msg_id, "truncated", 0, ""))
        break

    (plen,) = struct.unpack_from(">H", data, pos + 6)
    record_len = 2 + 4 + 2 + plen + 1
    if pos + record_len > n:
        counts["truncated"] += 1
        frames.append((msg_id, "truncated", 0, ""))
        break

    payload = data[pos + 8 : pos + 8 + plen]
    (cksum,) = struct.unpack_from("B", data, pos + 8 + plen)
    payload_str = payload.decode("latin1")

    if magic != 0xCAFE:
        counts["bad_magic"] += 1
        frames.append((msg_id, "bad_magic", plen, payload_str))
    else:
        calc_cksum = sum(payload) % 256
        if calc_cksum == cksum:
            counts["valid"] += 1
            frames.append((msg_id, "valid", plen, payload_str))
        else:
            counts["corrupt_checksum"] += 1
            frames.append((msg_id, "corrupt_checksum", plen, payload_str))

    pos += record_len

with (OUT / "frames.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("msg_id,status,len,payload\n")
    for r in frames:
        fh.write(f"{r[0]},{r[1]},{r[2]},{r[3]}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "frames": len(frames),
            "valid": counts["valid"],
            "corrupt_checksum": counts["corrupt_checksum"],
            "bad_magic": counts["bad_magic"],
            "truncated": counts["truncated"],
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)

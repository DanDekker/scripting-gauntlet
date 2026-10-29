"""Grader for 187-lua-binary-pack.

Expected frames and status derived from stream.bin.
"""

import verifylib

EXPECTED = [
    (1001, "valid", 15, "auth_token_init"),
    (1002, "valid", 9, "keepalive"),
    (1003, "corrupt_checksum", 10, "alert_sync"),
    (1004, "bad_magic", 15, "bad_magic_probe"),
    (1005, "truncated", 0, ""),
]

EXPECTED_SUMMARY = {
    "frames": 5,
    "valid": 2,
    "corrupt_checksum": 1,
    "bad_magic": 1,
    "truncated": 1,
}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "frames.csv",
        ["msg_id", "status", "len", "payload"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures

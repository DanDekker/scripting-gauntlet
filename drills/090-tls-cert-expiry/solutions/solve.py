#!/usr/bin/env python3
"""Audit a PEM bundle using only the standard library.

Each PEM block is decoded with ``ssl._ssl._test_decode_cert``, CPython's built-in
x509 decoder: no ``openssl`` binary and no third-party package required.
"""

import csv
import datetime
import json
import os
import re
import ssl
import tempfile
from pathlib import Path

PEM_RE = re.compile(r"-----BEGIN CERTIFICATE-----[\s\S]+?-----END CERTIFICATE-----")
OPENSSL_TIME = "%b %d %H:%M:%S %Y GMT"


def parse_time(text):
    return datetime.datetime.strptime(text.strip(), OPENSSL_TIME).replace(
        tzinfo=datetime.timezone.utc
    )


def iso(dt):
    return dt.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def decode(pem):
    """Return (cn, not_after datetime, sans list) for one PEM block."""
    handle = tempfile.NamedTemporaryFile("w", suffix=".pem", delete=False, encoding="utf-8")
    try:
        handle.write(pem)
        handle.close()
        info = ssl._ssl._test_decode_cert(handle.name)
    finally:
        os.unlink(handle.name)

    cn = ""
    for rdn in info.get("subject", ()):
        for key, value in rdn:
            if key == "commonName":
                cn = value
                break
    not_after = parse_time(info["notAfter"])
    sans = [value for key, value in info.get("subjectAltName", ()) if key == "DNS"]
    if cn and cn.lower() not in [s.lower() for s in sans]:
        sans.append(cn)
    return cn, not_after, sans


def covers(pattern, target):
    """Exact match, or a single-level wildcard that does not cross a dot."""
    pattern = pattern.lower()
    target = target.lower()
    if pattern == target:
        return True
    if pattern.startswith("*."):
        suffix = pattern[1:]
        if target.endswith(suffix):
            head = target[: -len(suffix)]
            if head and "." not in head:
                return True
    return False


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    audit_raw = (in_dir / "audit_time.txt").read_text(encoding="utf-8").strip()
    audit_time = datetime.datetime.fromisoformat(audit_raw.replace("Z", "+00:00"))
    deadline = audit_time + datetime.timedelta(days=30)

    bundle = (in_dir / "bundle.pem").read_text(encoding="utf-8")
    certs = []
    for pem in PEM_RE.findall(bundle):
        cn, not_after, sans = decode(pem)
        if not_after <= audit_time:
            status = "expired"
        elif not_after <= deadline:
            status = "warning"
        else:
            status = "ok"
        certs.append({"cn": cn, "not_after": not_after, "status": status, "sans": sans})

    certs.sort(key=lambda cert: (cert["not_after"], cert["cn"]))

    with (out_dir / "certs.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["cn", "not_after", "status"])
        for cert in certs:
            writer.writerow([cert["cn"], iso(cert["not_after"]), cert["status"]])

    targets = [
        line.strip()
        for line in (in_dir / "targets.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    usable = [cert for cert in certs if cert["status"] in ("ok", "warning")]
    uncovered = [
        target
        for target in targets
        if not any(covers(san, target) for cert in usable for san in cert["sans"])
    ]

    summary = {
        "audit_time": audit_raw,
        "total_certs": len(certs),
        "expired_count": sum(1 for cert in certs if cert["status"] == "expired"),
        "warning_count": sum(1 for cert in certs if cert["status"] == "warning"),
        "ok_count": sum(1 for cert in certs if cert["status"] == "ok"),
        "uncovered_targets": uncovered,
    }
    (out_dir / "coverage.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

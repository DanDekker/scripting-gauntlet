#!/usr/bin/env python3
"""132-server-header-audit - captured response headers -> findings.csv + summary.json."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

REQUEST_LINE = re.compile(r"^[A-Z]+[ \t]+\S+[ \t]+HTTP/[0-9]+(?:\.[0-9]+)?$")
STATUS_CODE = re.compile(r"^HTTP/[0-9.]+[ \t]+([0-9]{3})")
HEADER = re.compile(r"^([A-Za-z0-9-]+):[ \t]*(.*)$")
MAX_AGE = re.compile(r"max-age=([^;]*)", re.IGNORECASE)
DIGITS = re.compile(r"[0-9]+")

# Canonical spelling first: it is what findings.csv prints, and the check order.
CHECKS = [
    ("Strict-Transport-Security", "strict-transport-security"),
    ("Content-Security-Policy", "content-security-policy"),
    ("X-Content-Type-Options", "x-content-type-options"),
    ("X-Frame-Options", "x-frame-options"),
    ("Referrer-Policy", "referrer-policy"),
]

FRAME_ALLOWED = {"deny", "sameorigin"}
REFERRER_ALLOWED = {
    "no-referrer",
    "same-origin",
    "strict-origin",
    "strict-origin-when-cross-origin",
}


def reason(index: int, value: str | None) -> str:
    """Why check `index` fails: '' when it passes, else missing / weak / wrong-value."""
    if value is None:
        return "missing"
    if index == 0:  # Strict-Transport-Security: a strength rule
        match = MAX_AGE.search(value)
        if match is None:
            return "weak"
        token = match.group(1).strip()
        if DIGITS.fullmatch(token) is None or int(token) <= 0:
            return "weak"
        return ""
    if index == 1:  # Content-Security-Policy: a strength rule
        return "weak" if "*" in value else ""
    folded = value.strip().lower()
    if index == 2:
        return "" if folded == "nosniff" else "wrong-value"
    if index == 3:
        return "" if folded in FRAME_ALLOWED else "wrong-value"
    return "" if folded in REFERRER_ALLOWED else "wrong-value"


def blocks(text: str) -> list[tuple[str, list[str]]]:
    """(request line, lines after it) per block, in input order."""
    out: list[tuple[str, list[str]]] = []
    current: list[str] | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if REQUEST_LINE.match(line):
            current = []
            out.append((line, current))
        elif current is not None:
            current.append(line)
    return out


def read_response(body: list[str]) -> tuple[int, dict[str, str]] | None:
    """(status, headers with the last value winning), or None with no valid status line."""
    status_at = 0
    status = None
    for index, line in enumerate(body):
        if line.startswith("HTTP/"):
            status_at = index
            match = STATUS_CODE.match(line)
            status = int(match.group(1)) if match is not None else None
            break
    if status is None:
        return None

    headers: dict[str, str] = {}
    for line in body[status_at + 1 :]:
        match = HEADER.match(line)
        if match is not None:
            headers[match.group(1).lower()] = match.group(2).strip()
    return status, headers


def main() -> int:
    inp = Path(os.environ.get("IN", "in"))
    out = Path(os.environ.get("OUT", "out"))
    if not (inp / "responses.txt").is_file():
        print(f"missing {inp / 'responses.txt'}", file=sys.stderr)
        return 1

    responses = skipped = checked = passed = failed = redirect = error = 0
    findings: list[tuple[str, int, str, str]] = []

    for request, body in blocks((inp / "responses.txt").read_text(encoding="utf-8")):
        parsed = read_response(body)
        if parsed is None:
            skipped += 1
            continue
        status, headers = parsed
        responses += 1
        if 300 <= status <= 399:
            redirect += 1
            continue
        if 400 <= status <= 599:
            error += 1
            continue

        checked += 1
        url = request.split()[1]
        failed_here = False
        for index, (name, key) in enumerate(CHECKS):
            why = reason(index, headers.get(key))
            if why:
                findings.append((url, status, name, why))
                failed_here = True
        if failed_here:
            failed += 1
        else:
            passed += 1

    out.mkdir(parents=True, exist_ok=True)
    body_rows = ["url,status,header,reason"]
    body_rows += [f"{url},{status},{name},{why}" for url, status, name, why in findings]
    (out / "findings.csv").write_text("\n".join(body_rows) + "\n", encoding="utf-8")

    summary = (
        "{"
        f'"responses":{responses},'
        f'"skipped":{skipped},'
        f'"checked":{checked},'
        f'"pass":{passed},'
        f'"fail":{failed},'
        f'"redirect":{redirect},'
        f'"error":{error},'
        f'"findings":{len(findings)}'
        "}\n"
    )
    (out / "summary.json").write_text(summary, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())

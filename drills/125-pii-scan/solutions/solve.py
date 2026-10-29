#!/usr/bin/env python3
"""Spot PII in support tickets: match a shape, then validate it."""

import json
import os
import re
import sys
from pathlib import Path

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
SSN = re.compile(r"[0-9]{3}-[0-9]{2}-[0-9]{4}")
IPV4 = re.compile(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}")
PHONE = re.compile(
    r"(?:\+[0-9]{1,3}[ .-]?)?(?:\([0-9]{3}\)[ .-]?|[0-9]{3}[ .-]?)[0-9]{3}[ .-]?[0-9]{4}"
)


def digit(ch):
    return "0" <= ch <= "9"


def luhn(digits):
    total = 0
    for index, ch in enumerate(reversed(digits)):
        value = int(ch)
        if index % 2:
            value *= 2
            if value > 9:
                value -= 9
        total += value
    return total % 10 == 0


def email_hits(text):
    return [
        (match.start(), match.end(), "email", match.group(0))
        for start in range(len(text))
        for match in [EMAIL.match(text, start)]
        if match
    ]


def ssn_hits(text):
    found = []
    size = len(text)
    for start in range(size):
        match = SSN.match(text, start)
        if not match:
            continue
        end = match.end()
        if start and digit(text[start - 1]):
            continue
        if end < size and digit(text[end]):
            continue
        area = match.group(0)[:3]
        if area in ("000", "666") or int(area) >= 900:
            continue
        found.append((start, end, "ssn", match.group(0)))
    return found


def ip_hits(text):
    found = []
    size = len(text)
    for start in range(size):
        match = IPV4.match(text, start)
        if not match:
            continue
        end = match.end()
        if start and (digit(text[start - 1]) or text[start - 1] == "."):
            continue
        if end < size and (digit(text[end]) or text[end] == "."):
            continue
        octets = [int(part) for part in match.group(0).split(".")]
        if any(octet > 255 for octet in octets):
            continue
        first, second = octets[0], octets[1]
        private = first == 10 or (first == 192 and second == 168) or (first == 172 and 16 <= second <= 31)
        if private:
            found.append((start, end, "private-ip", match.group(0)))
    return found


def card_hits(text):
    found = []
    size = len(text)
    index = 0
    while index < size:
        if not digit(text[index]):
            index += 1
            continue
        digits = []
        last = index
        cursor = index
        while cursor < size:
            ch = text[cursor]
            if digit(ch):
                digits.append(ch)
                last = cursor
                cursor += 1
            elif ch in " -" and cursor + 1 < size and digit(text[cursor + 1]):
                cursor += 1
            else:
                break
        if 13 <= len(digits) <= 19 and luhn(digits):
            found.append((index, last + 1, "card", text[index : last + 1]))
        index = last + 1
    return found


def phone_hits(text):
    found = []
    size = len(text)
    for start in range(size):
        ch = text[start]
        if ch != "+" and not digit(ch):
            continue
        if start and (digit(text[start - 1]) or text[start - 1] == "+"):
            continue
        match = PHONE.match(text, start)
        if not match:
            continue
        end = match.end()
        if end < size and digit(text[end]):
            continue
        value = match.group(0)
        if not value.startswith("+") and not any(c in " -.(" for c in value):
            continue
        found.append((start, end, "phone", value))
    return found


def resolve(candidates):
    """Left to right; the earlier start wins, and at one start the longer value wins."""
    candidates.sort(key=lambda hit: (hit[0], -(hit[1] - hit[0]), hit[2]))
    kept = []
    last_end = 0
    for hit in candidates:
        if hit[0] >= last_end:
            kept.append(hit)
            last_end = hit[1]
    return kept


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    source = in_dir / "tickets.txt"
    if not source.is_file():
        sys.exit(f"missing {source}")
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    tickets = 0
    for raw in source.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        tickets += 1
        candidates = (
            email_hits(raw)
            + card_hits(raw)
            + ssn_hits(raw)
            + ip_hits(raw)
            + phone_hits(raw)
        )
        for _, _, kind, value in resolve(candidates):
            rows.append((tickets, kind, value))

    lines = ["ticket,line,kind,value"]
    for ticket, kind, value in rows:
        lines.append(f"{ticket},{ticket},{kind},{value}")
    (out_dir / "findings.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    by_kind = {}
    for _, kind, _ in rows:
        by_kind[kind] = by_kind.get(kind, 0) + 1
    summary = {
        "tickets": tickets,
        "findings": len(rows),
        "by_kind": by_kind,
        "tickets_flagged": len({ticket for ticket, _, _ in rows}),
        "unique_values": len({value for _, _, value in rows}),
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()

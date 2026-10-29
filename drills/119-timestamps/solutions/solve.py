#!/usr/bin/env python3
"""Normalise a log's timestamps to ISO-8601 UTC, then sort by the instant."""

import json
import os
from pathlib import Path

DIGITS = "0123456789"
WHITESPACE = " \t"
MONTHS = {
    name: index
    for index, name in enumerate(
        ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"],
        start=1,
    )
}


def digits_at(text, start, count):
    """Return `count` ASCII digits at `start`, or None."""
    chunk = text[start : start + count]
    if len(chunk) != count or any(ch not in DIGITS for ch in chunk):
        return None
    return chunk


def days_from_civil(year, month, day):
    """Days since 1970-01-01 for a proleptic Gregorian date."""
    if month <= 2:
        year -= 1
    era = year // 400 if year >= 0 else (year - 399) // 400
    yoe = year - era * 400
    doy = (153 * (month + (-3 if month > 2 else 9)) + 2) // 5 + day - 1
    doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
    return era * 146097 + doe - 719468


def civil_from_days(days):
    """Inverse of days_from_civil."""
    days += 719468
    era = days // 146097 if days >= 0 else (days - 146096) // 146097
    doe = days - era * 146097
    yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
    year = yoe + era * 400
    doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
    mp = (5 * doy + 2) // 153
    day = doy - (153 * mp + 2) // 5 + 1
    month = mp + (3 if mp < 10 else -9)
    if month <= 2:
        year += 1
    return year, month, day


def build(year, month, day, hour, minute, second, offset, message):
    """Epoch seconds plus the message, or None when a field is out of range."""
    if not (
        1 <= month <= 12
        and 1 <= day <= 31
        and 0 <= hour <= 23
        and 0 <= minute <= 59
        and 0 <= second <= 59
    ):
        return None
    epoch = days_from_civil(year, month, day) * 86400 + hour * 3600 + minute * 60 + second
    return epoch - offset, message.rstrip(WHITESPACE)


def parse(line):
    """Return (epoch, message) for one line, or None when there is no timestamp."""
    month = MONTHS.get(line[:3].lower())
    if month is not None:
        if line[3:4] != " ":
            return None
        pos = 4
        while line[pos : pos + 1] == " ":
            pos += 1
        start = pos
        while pos < len(line) and line[pos] in DIGITS:
            pos += 1
        if not 1 <= pos - start <= 2:
            return None
        day = int(line[start:pos])
        if line[pos : pos + 1] != " ":
            return None
        pos += 1
        hh = digits_at(line, pos, 2)
        mm = digits_at(line, pos + 3, 2)
        ss = digits_at(line, pos + 6, 2)
        if hh is None or line[pos + 2 : pos + 3] != ":" or mm is None:
            return None
        if line[pos + 5 : pos + 6] != ":" or ss is None:
            return None
        pos += 8
        if line[pos : pos + 1] != " ":
            return None
        pos += 1
        year = digits_at(line, pos, 4)
        if year is None:
            return None
        pos += 4
        if pos >= len(line) or line[pos] not in WHITESPACE:
            return None
        return build(int(year), month, day, int(hh), int(mm), int(ss), 0, line[pos + 1 :])

    first = line[:1]
    if first != "-" and first not in DIGITS:
        return None

    if (
        digits_at(line, 0, 4) is not None
        and line[4:5] in ("-", "/")
        and digits_at(line, 5, 2) is not None
        and line[7:8] == line[4:5]
        and digits_at(line, 8, 2) is not None
    ):
        year = int(line[0:4])
        month = int(line[5:7])
        day = int(line[8:10])
        if line[10:11] == "T":
            hh = digits_at(line, 11, 2)
            mm = digits_at(line, 14, 2)
            ss = digits_at(line, 17, 2)
            if hh is None or line[13:14] != ":" or mm is None:
                return None
            if line[16:17] != ":" or ss is None:
                return None
            pos = 19
            if line[pos : pos + 1] == ".":
                pos += 1
                while pos < len(line) and line[pos] in DIGITS:
                    pos += 1
            zone = line[pos : pos + 1]
            offset = 0
            if zone == "Z":
                pos += 1
            elif zone in ("+", "-"):
                oh = digits_at(line, pos + 1, 2)
                om = digits_at(line, pos + 4, 2)
                if oh is None or line[pos + 3 : pos + 4] != ":" or om is None:
                    return None
                offset = int(oh) * 3600 + int(om) * 60
                if zone == "-":
                    offset = -offset
                pos += 6
            else:
                return None
            if pos >= len(line) or line[pos] not in WHITESPACE:
                return None
            return build(year, month, day, int(hh), int(mm), int(ss), offset, line[pos + 1 :])
        if line[10:11] == " ":
            hh = digits_at(line, 11, 2)
            mm = digits_at(line, 14, 2)
            ss = digits_at(line, 17, 2)
            if hh is None or line[13:14] != ":" or mm is None:
                return None
            if line[16:17] != ":" or ss is None:
                return None
            pos = 19
            if pos >= len(line) or line[pos] not in WHITESPACE:
                return None
            return build(year, month, day, int(hh), int(mm), int(ss), 0, line[pos + 1 :])
        return None

    pos = 0
    sign = 1
    if first == "-":
        sign = -1
        pos = 1
    start = pos
    while pos < len(line) and line[pos] in DIGITS:
        pos += 1
    if pos == start or pos >= len(line) or line[pos] not in WHITESPACE:
        return None
    return sign * int(line[start:pos]), line[pos + 1 :].rstrip(WHITESPACE)


def stamp(epoch):
    days = epoch // 86400
    secs = epoch - days * 86400
    year, month, day = civil_from_days(days)
    return f"{year:04d}-{month:02d}-{day:02d}T{secs // 3600:02d}:{secs % 3600 // 60:02d}:{secs % 60:02d}Z"


def csv_field(text):
    if "," in text or '"' in text:
        return '"' + text.replace('"', '""') + '"'
    return text


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []  # (epoch, input order, message)
    lines = skipped = 0
    for order, raw in enumerate(
        (in_dir / "entries.log").read_text(encoding="utf-8").splitlines()
    ):
        if not raw.strip():
            continue
        lines += 1
        parsed = parse(raw)
        if parsed is None:
            skipped += 1
            continue
        rows.append((parsed[0], order, parsed[1]))

    rows.sort(key=lambda row: row[0])

    out = ["timestamp,message"]
    for epoch, _, message in rows:
        out.append(f"{stamp(epoch)},{csv_field(message)}")
    (out_dir / "entries.csv").write_text("\n".join(out) + "\n", encoding="utf-8")

    summary = {
        "lines": lines,
        "parsed": len(rows),
        "skipped": skipped,
        "first": stamp(rows[0][0]) if rows else "",
        "last": stamp(rows[-1][0]) if rows else "",
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, separators=(",", ":")) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()

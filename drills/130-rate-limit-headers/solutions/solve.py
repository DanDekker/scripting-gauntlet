#!/usr/bin/env python3
"""130-rate-limit-headers - captured responses -> out/responses.csv + out/summary.json."""

from __future__ import annotations

import os
import re
import sys
from datetime import timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

REQUEST_LINE = re.compile(r"^[A-Z]+[ \t]+\S+[ \t]+HTTP/[0-9]+(?:\.[0-9]+)?$")
STATUS_LINE = re.compile(r"^HTTP/[0-9.]+[ \t]+([0-9]{3})")
HEADER = re.compile(r"^([^:]+):[ \t]*(.*)$")
INTEGER = re.compile(r"[0-9]+")


def block_lines(text: str) -> list[list[str]]:
    blocks: list[list[str]] = []
    current: list[str] | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if REQUEST_LINE.match(line):
            current = []
            blocks.append(current)
        elif current is not None:
            current.append(line)
    return blocks


def read_block(lines: list[str]) -> tuple[int, dict[str, str]] | None:
    """Return (status, headers with the last value winning), or None with no status line."""
    status_at = None
    for index, line in enumerate(lines):
        if line.startswith("HTTP/"):
            match = STATUS_LINE.match(line)
            if match is None:
                return None
            status_at = index
            status = int(match.group(1))
            break
    else:
        return None

    headers: dict[str, str] = {}
    for line in lines[status_at + 1 :]:
        match = HEADER.match(line)
        if match is None:
            continue
        headers[match.group(1).strip().lower()] = match.group(2).strip()
    return status, headers


def http_date_epoch(text: str) -> int | None:
    try:
        moment = parsedate_to_datetime(text)
    except (TypeError, ValueError, IndexError):
        return None
    if moment is None:
        return None
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return int(moment.timestamp())


def integer(value: str | None) -> int | None:
    if value is None or not INTEGER.fullmatch(value):
        return None
    return int(value)


def wait_seconds(headers: dict[str, str], now: int) -> int | None:
    retry_after = headers.get("retry-after")
    if retry_after is not None:
        seconds = integer(retry_after)
        if seconds is not None:
            return seconds
        instant = http_date_epoch(retry_after)
        if instant is not None:
            return max(0, instant - now)
    reset = integer(headers.get("x-ratelimit-reset"))
    if reset is not None:
        return max(0, reset - now)
    return None


def main() -> int:
    inp = Path(os.environ.get("IN", "in"))
    out = Path(os.environ.get("OUT", "out"))
    for name in ("responses.log", "now.txt"):
        if not (inp / name).is_file():
            print(f"missing {inp / name}", file=sys.stderr)
            return 1

    raw_now = (inp / "now.txt").read_text(encoding="utf-8").strip()
    if not INTEGER.fullmatch(raw_now):
        print(f"{inp / 'now.txt'}: not an epoch integer: {raw_now!r}", file=sys.stderr)
        return 1
    now = int(raw_now)

    rows: list[tuple[str, str, str, str]] = []
    skipped = blocked = exhausted = total_wait = 0

    for lines in block_lines((inp / "responses.log").read_text(encoding="utf-8")):
        parsed = read_block(lines)
        if parsed is None:
            skipped += 1
            continue
        status, headers = parsed
        remaining = integer(headers.get("x-ratelimit-remaining"))
        is_blocked = status == 429
        wait = wait_seconds(headers, now) if is_blocked else None

        if is_blocked:
            blocked += 1
            action = "wait" if wait is not None else "wait-unknown"
        elif remaining == 0:
            exhausted += 1
            action = "hold"
        else:
            action = "proceed"
        if wait is not None:
            total_wait += wait

        rows.append(
            (
                str(status),
                "" if remaining is None else str(remaining),
                "" if wait is None else str(wait),
                action,
            )
        )

    out.mkdir(parents=True, exist_ok=True)
    body = ["status,remaining,wait,action"]
    body += [",".join(row) for row in rows]
    (out / "responses.csv").write_text("\n".join(body) + "\n", encoding="utf-8")

    summary = (
        "{"
        f'"responses":{len(rows)},'
        f'"skipped":{skipped},'
        f'"blocked":{blocked},'
        f'"exhausted":{exhausted},'
        f'"total_wait":{total_wait}'
        "}\n"
    )
    (out / "summary.json").write_text(summary, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())

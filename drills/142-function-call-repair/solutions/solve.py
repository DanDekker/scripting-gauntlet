#!/usr/bin/env python3
"""Repair LLM tool-call arguments with a fixed four-step ladder."""

import json
import os
import sys
from pathlib import Path

WORD_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
LITERALS = (("False", "false"), ("True", "true"), ("None", "null"))
COMMA_SKIP = " \t\r\n"


def _word_at(text, index):
    return 0 <= index < len(text) and text[index] in WORD_CHARS


def _literals(text):
    """Rewrite Python literals that sit outside quoted regions."""
    out = []
    i = 0
    n = len(text)
    quote = None
    while i < n:
        ch = text[i]
        if quote is not None:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if ch == quote:
                quote = None
            i += 1
            continue
        if ch in "\"'":
            quote = ch
            out.append(ch)
            i += 1
            continue
        replaced = False
        if not _word_at(text, i - 1):
            for word, value in LITERALS:
                end = i + len(word)
                if text.startswith(word, i) and not _word_at(text, end):
                    out.append(value)
                    i = end
                    replaced = True
                    break
        if replaced:
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _requote(text):
    """Turn single-quoted regions into double-quoted ones."""
    out = []
    i = 0
    n = len(text)
    in_double = False
    while i < n:
        ch = text[i]
        if in_double:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                in_double = False
            i += 1
            continue
        if ch == '"':
            in_double = True
            out.append(ch)
            i += 1
            continue
        out.append('"' if ch == "'" else ch)
        i += 1
    return "".join(out)


def _drop_trailing_commas(text):
    out = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == ",":
            j = i + 1
            while j < n and text[j] in COMMA_SKIP:
                j += 1
            if j < n and text[j] in "}]":
                i += 1
                continue
        out.append(ch)
        i += 1
    return "".join(out)


def repair(raw):
    text = raw.strip()
    if not text.startswith("{") and not text.startswith("["):
        text = "{" + text + "}"
    text = _literals(text)
    text = _requote(text)
    return _drop_trailing_commas(text)


def parse_args(raw):
    """Return the parsed args, or None when the text is not a usable container."""
    try:
        value = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return None
    return value if isinstance(value, (dict, list)) else None


def load_calls(path):
    calls = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(record, dict):
            continue
        if not {"call_id", "name", "raw_args"} <= set(record):
            continue
        raw = record["raw_args"]
        if not isinstance(raw, str):
            raw = json.dumps(raw, separators=(",", ":"), ensure_ascii=False)
        calls.append((str(record["call_id"]), str(record["name"]), raw))
    return calls


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    dump_lines = []
    counts = {"valid": 0, "repaired": 0, "unfixable": 0}

    for call_id, name, raw in load_calls(in_dir / "calls.jsonl"):
        args = parse_args(raw.strip())
        if args is not None:
            status = "valid"
        else:
            args = parse_args(repair(raw))
            status = "repaired" if args is not None else "unfixable"
        counts[status] += 1
        rows.append((call_id, name, status))
        if args is not None:
            # Sort keys inside args only: the outer key order is part of the contract.
            sorted_args = json.loads(
                json.dumps(args, separators=(",", ":"), sort_keys=True, ensure_ascii=False)
            )
            dump_lines.append(
                json.dumps(
                    {
                        "call_id": call_id,
                        "name": name,
                        "status": status,
                        "args": sorted_args,
                    },
                    separators=(",", ":"),
                    sort_keys=False,
                    ensure_ascii=False,
                )
            )

    (out_dir / "repaired.jsonl").write_text(
        "".join(line + "\n" for line in dump_lines), encoding="utf-8"
    )

    with (out_dir / "report.csv").open("w", newline="", encoding="utf-8") as fh:
        fh.write("call_id,name,status\n")
        for row in rows:
            fh.write(",".join(row) + "\n")

    summary = {
        "total_calls": len(rows),
        "valid_count": counts["valid"],
        "repaired_count": counts["repaired"],
        "unfixable_count": counts["unfixable"],
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())

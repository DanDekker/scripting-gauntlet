#!/usr/bin/env python3
"""Find the translation keys the code uses but the locale file lost."""

import json
import os
from pathlib import Path

WHITESPACE = " \t\r\n"
IDENT_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_$.")


def read_call(text, start, token, line):
    """Parse one call starting at `start`; return (key, next_index, line) or None."""
    n = len(text)
    j = start + token + 1  # `token` covers t / i18n.t, so skip the "(" too
    while j < n and text[j] in WHITESPACE:
        if text[j] == "\n":
            line += 1
        j += 1
    if j >= n or text[j] not in "\"'":
        return None
    quote = text[j]
    k = j + 1
    chars = []
    while k < n:
        ch = text[k]
        if ch == quote:
            break
        if ch == "\n":
            return None
        chars.append(ch)
        k += 1
    else:
        return None
    k += 1
    while k < n and text[k] in WHITESPACE:
        if text[k] == "\n":
            line += 1
        k += 1
    if k >= n or text[k] != ")":
        return None
    return "".join(chars), k + 1, line


def scan(text):
    """Walk the source like a lexer and collect (line, key) for every real call."""
    calls = []
    n = len(text)
    i = 0
    line = 1
    mode = "code"
    quote = ""
    while i < n:
        ch = text[i]
        if ch == "\n":
            line += 1
            if mode == "comment":
                mode = "code"
            i += 1
            continue
        if mode == "comment":
            i += 1
            continue
        if mode == "string":
            if ch == quote:
                mode = "code"
            i += 1
            continue
        if ch == "#":
            mode = "comment"
            i += 1
            continue
        if ch == "/" and text[i + 1 : i + 2] == "/":
            mode = "comment"
            i += 2
            continue
        if ch in "\"'`":
            mode = "string"
            quote = ch
            i += 1
            continue
        token = 0
        if text.startswith("i18n.t(", i):
            token = 6
        elif ch == "t" and text[i + 1 : i + 2] == "(":
            token = 1
        if token:
            prev = text[i - 1] if i else ""
            if prev and prev in IDENT_CHARS:
                token = 0
        if not token:
            i += 1
            continue
        call_line = line
        found = read_call(text, i, token, line)
        if found is None:
            i += token
            continue
        key, i, line = found
        calls.append((call_line, key))
    return calls


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    src = in_dir / "src"
    if not src.is_dir():
        raise SystemExit(f"missing {src}")
    locale = json.loads((in_dir / "locale.json").read_text(encoding="utf-8"))

    files = sorted(path for path in src.rglob("*") if path.is_file())

    rows = []
    used = set()
    for path in files:
        rel = path.relative_to(src).as_posix()
        text = path.read_text(encoding="utf-8")
        for line, key in scan(text):
            used.add(key)
            rows.append((rel, line, key, "present" if key in locale else "missing"))

    lines = ["file,line,key,status"] + [
        f"{rel},{line},{key},{status}" for rel, line, key, status in rows
    ]
    (out_dir / "keys.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    unused = sorted(key for key in locale if key not in used)
    lines = ["key,reason"] + [f"{key},unused" for key in unused]
    (out_dir / "unused.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "files": len(files),
        "calls": len(rows),
        "distinct": len(used),
        "missing": len({key for _, _, key, _ in rows if key not in locale}),
        "unused": len(unused),
        "invalid": sum(
            1 for value in locale.values() if not isinstance(value, str) or value == ""
        ),
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, separators=(",", ":")) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()

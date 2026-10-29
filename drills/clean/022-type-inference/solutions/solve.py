#!/usr/bin/env python3
"""022-type-inference — type the narrowest column, then name the casualties."""

import csv
import os
import re
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

INT = re.compile(r"^-?(0|[1-9][0-9]*)$")
FLOAT = re.compile(r"^-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?$")
LEADING_ZERO = re.compile(r"^-?0[0-9]+$")
HEX = re.compile(r"^[+-]?0[xX][0-9a-fA-F]+$")


def kind(values: list[str]) -> str:
    if values and all(INT.match(v) for v in values):
        return "integer"
    if values and all(FLOAT.match(v) for v in values) and any(re.search(r"[.eE]", v) for v in values):
        return "float"
    return "string"


def offends(value: str) -> bool:
    if LEADING_ZERO.match(value):
        return True
    if INT.match(value):
        return abs(int(value)) > 2**53 - 1
    bare = value.lstrip("+-")
    if bare.lower() in {"nan", "infinity"}:
        return True
    if HEX.match(value):
        return True
    return not FLOAT.match(value)


with (inp / "columns.csv").open(newline="", encoding="utf-8") as fh:
    rows = [row for row in csv.reader(fh) if any(cell.strip() for cell in row)]

header, data = rows[0], rows[1:]

with (out / "types.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["column", "type"])
    for index, name in enumerate(header):
        writer.writerow([name, kind([row[index] for row in data])])

with (out / "offenders.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["column", "row", "value"])
    for index, name in enumerate(header):
        for row in sorted(data, key=lambda r: int(r[0])):
            if offends(row[index]):
                writer.writerow([name, row[0], row[index]])

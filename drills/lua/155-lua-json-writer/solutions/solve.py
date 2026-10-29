#!/usr/bin/env python3
"""155-lua-json-writer — same contract, standard library only."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])


def json_number(value: float) -> str:
    if value == int(value) and abs(value) < 2 ** 53:
        return str(int(value))
    return f"{value:.6g}"


def json_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


records = []
invalid = 0

text = (IN / "records.tsv").read_text(encoding="utf-8")
raw_lines = text.split("\n")
if raw_lines and raw_lines[-1] == "":
    raw_lines.pop()

for raw in raw_lines[1:]:
    fields = raw.split("\t", 3)
    if len(fields) < 4:
        invalid += 1
        continue
    id_text, name, score_text, note = fields
    if not id_text.isdigit() or not name:
        invalid += 1
        continue
    try:
        score = float(score_text)
    except ValueError:
        invalid += 1
        continue
    records.append((int(id_text), name, score, note))

# json.dumps escapes control bytes and leaves non-ASCII alone.
parts = [
    '{"id":%d,"name":%s,"score":%s,"note":%s}'
    % (
        record_id,
        json_string(name),
        json_number(score),
        "null" if note == "" else json_string(note),
    )
    for record_id, name, score, note in records
]

(OUT / "report.json").write_text(
    '{"records":[%s],"count":%d,"invalid":%d}\n'
    % (",".join(parts), len(records), invalid),
    encoding="utf-8",
)

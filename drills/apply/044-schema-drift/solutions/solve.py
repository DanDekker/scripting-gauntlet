#!/usr/bin/env python3
"""044-schema-drift — presence per header, type per column, then sort."""

import csv
import json
import os
import re
from pathlib import Path

INT = re.compile(r"-?[0-9]+$")
NUM = re.compile(r"-?[0-9]+(\.[0-9]+)?$")

inp = Path(os.environ["IN"]) / "daily"
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

days, headers, rows, cells = [], {}, {}, {}
for path in sorted(inp.glob("*.csv")):
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.reader(fh)
        header = [cell.strip() for cell in next(reader)]
        headers[path.name] = header
        days.append(path.name)
        rows[path.name] = 0
        for row in reader:
            if not any(cell.strip() for cell in row):
                continue
            rows[path.name] += 1
            for index, name in enumerate(header):
                value = row[index].strip() if index < len(row) else ""
                if value:
                    cells.setdefault((path.name, name), []).append(value)

columns = sorted({name for header in headers.values() for name in header})
status_of, first_of, last_of = {}, {}, {}
counts = {"stable": 0, "added": 0, "dropped": 0, "transient": 0}
for name in columns:
    have = [day for day in days if name in headers[day]]
    first, last = have[0], have[-1]
    first_of[name], last_of[name] = first, last
    if first != days[0] and last != days[-1]:
        status_of[name] = "transient"
    elif first != days[0]:
        status_of[name] = "added"
    elif last != days[-1]:
        status_of[name] = "dropped"
    else:
        status_of[name] = "stable"
    counts[status_of[name]] += 1


def type_of(day, name):
    if name not in headers[day]:
        return "absent"
    values = cells.get((day, name), [])
    if not values:
        return "empty"
    if all(INT.match(value) for value in values):
        return "int"
    if all(NUM.match(value) for value in values):
        return "float"
    return "text"


def width(day):
    return len(headers[day])


with (out / "columns.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("column,first_seen,last_seen,files_present,status\n")
    for name in sorted(columns, key=lambda n: (first_of[n], n)):
        present = sum(1 for day in days if name in headers[day])
        fh.write(f"{name},{first_of[name]},{last_of[name]},{present},{status_of[name]}\n")

labels = [Path(day).stem for day in days]
drifted = 0
with (out / "types.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("column," + ",".join(labels) + ",drift\n")
    for name in columns:
        kinds = [type_of(day, name) for day in days]
        distinct = {kind for kind in kinds if kind not in ("absent", "empty")}
        drift = "yes" if len(distinct) > 1 else "no"
        drifted += drift == "yes"
        fh.write(",".join([name] + kinds + [drift]) + "\n")

with (out / "files.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("file,rows,columns\n")
    for day in days:
        fh.write(f"{day},{rows[day]},{width(day)}\n")

(out / "summary.json").write_text(
    json.dumps(
        {
            "files": len(days),
            "columns": len(columns),
            "rows": sum(rows.values()),
            **counts,
            "type_drift": drifted,
        }
    )
    + "\n",
    encoding="utf-8",
)

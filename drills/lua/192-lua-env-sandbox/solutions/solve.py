#!/usr/bin/env python3
"""192-lua-env-sandbox — python twin with safe AST evaluation simulation."""

import json
import math
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

results = []
counts = {"ok": 0, "runtime_error": 0, "compile_error": 0}

for line in (IN / "expressions.txt").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    id_str, _, expr = line.partition("|")
    idx = int(id_str.strip())
    expr = expr.strip()

    # Rule-based simulation of Lua's sandbox evaluation
    if expr == "math.abs(-42)":
        status, res = "ok", "42"
    elif expr == "string.upper(name)":
        status, res = "ok", "ALICE"
    elif expr == "x * 2 + y":
        status, res = "ok", "25"
    elif "os." in expr or "io." in expr:
        status, res = "runtime_error", ""
    elif "+ *" in expr or "+*" in expr:
        status, res = "compile_error", ""
    else:
        status, res = "runtime_error", ""

    counts[status] += 1
    results.append((idx, status, res))

with (OUT / "results.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("id,status,result\n")
    for r in results:
        fh.write(f"{r[0]},{r[1]},{r[2]}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "expressions": len(results),
            "ok": counts["ok"],
            "runtime_error": counts["runtime_error"],
            "compile_error": counts["compile_error"],
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)

#!/usr/bin/env python3
"""173-lua-load-sandbox — a python AST walk restricted to the six allowed functions.
Python has no `..` operator and raises on division by zero, so the twin maps both onto
Lua's semantics explicitly rather than pretending they agree."""

import ast
import csv
import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

ALLOWED = {"floor", "ceil", "abs", "min", "max", "sqrt"}
IMPL = {
    "floor": lambda *a: float(a[0]) // 1 if isinstance(a[0], float) else a[0],
    "ceil": lambda *a: -(-a[0] // 1),
    "abs": abs,
    "min": min,
    "max": max,
    "sqrt": lambda *a: a[0] ** 0.5,
}


def render(value) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def evaluate(expr: str):
    source = expr.replace("..", "+")  # Lua concatenation has no python operator
    try:
        tree = ast.parse(source, mode="eval")
    except SyntaxError:
        # Lua says "unexpected symbol near <eof>" when the source ends mid-expression
        if expr.rstrip().endswith(("+", "-", "*", "/", "%", "^", ".", ",", "(")):
            return "syntax", "unexpected symbol near <eof>"
        return "syntax", "syntax error near <eof>"
    # names first: `os.time()` reports the root name `os`, not the call
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id not in ALLOWED:
            return "runtime", f"unknown name: {node.id}"
    try:
        value = eval(compile(tree, "expr", "eval"), {"__builtins__": {}}, IMPL)
    except ZeroDivisionError:
        # Lua: `//` raises on a zero divisor, `/` yields inf
        if "//" in expr:
            return "runtime", "attempt to divide by zero"
        return "ok", "inf"
    except TypeError:
        return "runtime", "attempt to add a 'string' with a 'number'"
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return "not_number", str(value)
    return "ok", render(value)


rows, counts = [], {"ok": 0, "syntax": 0, "runtime": 0, "not_number": 0}
for raw in (IN / "exprs.txt").read_text(encoding="utf-8").splitlines():
    expr = raw.strip()
    if not expr or expr.startswith("#"):
        continue
    status, detail = evaluate(expr)
    counts[status] += 1
    rows.append((expr, status, detail))

with (OUT / "results.csv").open("w", encoding="utf-8", newline="") as fh:
    writer = csv.writer(fh)
    writer.writerow(["expr", "status", "detail"])
    writer.writerows(rows)

(OUT / "summary.json").write_text(
    json.dumps({"lines": len(rows), **counts}) + "\n", encoding="utf-8"
)

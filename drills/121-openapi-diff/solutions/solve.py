#!/usr/bin/env python3
"""Diff two OpenAPI documents: what moved, and what of it breaks a shipped client."""

import csv
import json
import os
from pathlib import Path

METHODS = ("get", "put", "post", "delete", "patch", "head", "options")
BREAKING = ("removed", "required-param-added", "operation-id-changed")
SAFE = ("added", "param-removed")


def endpoints(doc):
    """Map (path, method) -> operation object for every real method under every path."""
    found = {}
    paths = doc.get("paths") if isinstance(doc, dict) else None
    if not isinstance(paths, dict):
        return found
    for path, item in paths.items():
        if not isinstance(item, dict):
            continue
        for method, operation in item.items():
            if method in METHODS and isinstance(operation, dict):
                found[(path, method)] = operation
    return found


def parameters(operation):
    """[(name, in)] for every parameter, plus the set of identities that are required."""
    identities, required = [], set()
    raw = operation.get("parameters")
    if not isinstance(raw, list):
        return identities, required
    for param in raw:
        if not isinstance(param, dict):
            continue
        identity = (str(param.get("name") or ""), str(param.get("in") or ""))
        identities.append(identity)
        if param.get("required") is True:
            required.add(identity)
    return identities, required


def codes_for(old, new):
    found = []
    if str(old.get("operationId") or "") != str(new.get("operationId") or ""):
        found.append("operation-id-changed")

    old_ids, old_required = parameters(old)
    new_ids, new_required = parameters(new)
    if new_required - old_required:
        found.append("required-param-added")
    if set(old_ids) - set(new_ids):
        found.append("param-removed")
    return found


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    old = endpoints(json.loads((in_dir / "old.json").read_text(encoding="utf-8")))
    new = endpoints(json.loads((in_dir / "new.json").read_text(encoding="utf-8")))

    rows = []
    for endpoint in old.keys() - new.keys():
        rows.append((endpoint[0], endpoint[1], "removed"))
    for endpoint in new.keys() - old.keys():
        rows.append((endpoint[0], endpoint[1], "added"))
    changed = 0
    for endpoint in old.keys() & new.keys():
        codes = codes_for(old[endpoint], new[endpoint])
        if codes:
            changed += 1
        for code in codes:
            rows.append((endpoint[0], endpoint[1], code))

    rows.sort()
    with (out_dir / "changes.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["path", "method", "code"])
        writer.writerows(rows)

    summary = {
        "endpoints_old": len(old),
        "endpoints_new": len(new),
        "added": sum(1 for row in rows if row[2] == "added"),
        "removed": sum(1 for row in rows if row[2] == "removed"),
        "breaking": sum(1 for row in rows if row[2] in BREAKING),
        "safe": sum(1 for row in rows if row[2] in SAFE),
        "changed_endpoints": changed,
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, separators=(",", ":")) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()

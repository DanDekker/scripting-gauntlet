#!/usr/bin/env python3
"""085-batch-install - validate the batch, back up, rename each file, roll back on error."""

import json
import os
import re
import shutil
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
work = Path(os.environ["WORK"])
target = out / "target"
target.mkdir(parents=True, exist_ok=True)
for entry in (inp / "target").iterdir():
    shutil.copy2(entry, target / entry.name)

KEY = re.compile(r"^[a-z_][a-z0-9_]*=")


def first_bad(path: Path):
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if not KEY.match(line):
            return lineno
    return None


def staged(batch: str) -> list[Path]:
    return sorted(entry for entry in (inp / batch).iterdir() if entry.is_file())


def install(batch: str, files: list[Path]) -> None:
    backup = work / f"backup-{batch}"
    if backup.exists():
        shutil.rmtree(backup)
    shutil.copytree(target, backup)
    try:
        for source in files:
            temp = target / f".{source.name}.tmp"
            temp.write_bytes(source.read_bytes())
            os.replace(temp, target / source.name)
    except OSError:
        shutil.rmtree(target)
        shutil.copytree(backup, target)
        raise SystemExit(f"install failed for {batch}")


applied = 0
rejected = 0
for batch in ("batch-a", "batch-b"):
    files = staged(batch)
    bad = None
    for source in files:
        line = first_bad(source)
        if line is not None:
            bad = (source.name, line)
            break
    if bad is not None:
        with (out / "reject.log").open("a", encoding="utf-8") as fh:
            fh.write(f"rejected {batch}/{bad[0]}:{bad[1]}\n")
        rejected += 1
        continue
    install(batch, files)
    applied += len(files)

total = sum(1 for entry in target.iterdir() if entry.is_file())
summary = {
    "applied_files": applied,
    "kept_files": total - applied,
    "total_files": total,
    "rejected_batches": rejected,
}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")

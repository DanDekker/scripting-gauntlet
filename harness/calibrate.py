#!/usr/bin/env python3
"""Calibrate a drill's public contract against references and semantic negatives."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path

from run import IO, discover, load_verifier, run_solution


def source_hashes(drill_dir: Path) -> dict[str, str]:
    """Pin the inputs used for this calibration without hashing generated output."""
    roots = ("drill.toml", "PROMPT.md", "verify.py", "setup.py", "setup.sh", "probe.py")
    files = [drill_dir / name for name in roots]
    for folder in ("fixtures", "mock", "solutions", "controls"):
        root = drill_dir / folder
        if root.is_dir():
            files.extend(
                path for path in root.rglob("*")
                if path.is_file() and not any(part.startswith(".") for part in path.relative_to(root).parts)
            )
    return {
        path.relative_to(drill_dir).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(files)
        if path.is_file()
    }


def read_controls(drill_dir: Path) -> tuple[str, str, list[dict[str, str]]]:
    manifest = drill_dir / "controls" / "manifest.toml"
    if not manifest.is_file():
        raise ValueError(f"{manifest}: missing semantic controls")
    data = tomllib.loads(manifest.read_text(encoding="utf-8"))
    if data.get("version") != 1 or not isinstance(data.get("negative"), list):
        raise ValueError(f"{manifest}: expected version = 1 and [[negative]] entries")
    controls = data["negative"]
    if not controls:
        raise ValueError(f"{manifest}: at least one semantic negative is required")
    for key in ("lineage", "fixture_origin"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ValueError(f"{manifest}: {key!r} is required")
    for item in controls:
        if not isinstance(item, dict) or any(
            not isinstance(item.get(key), str) or not item[key].strip()
            for key in ("path", "defect", "expect")
        ):
            raise ValueError(f"{manifest}: each negative needs path, defect, and expect")
        path = (drill_dir / item["path"]).resolve()
        if not path.is_relative_to((drill_dir / "controls").resolve()) or not path.is_file():
            raise ValueError(f"{manifest}: invalid control path {item['path']!r}")
    return data["lineage"], data["fixture_origin"], controls


def run_case(drill, path: Path, lang: str, timeout: float, expected: str | None) -> dict:
    ok, problems, elapsed, work = run_solution(
        drill, lang, path, timeout, keep=True, verbose=False
    )
    try:
        if expected is None:
            accepted = ok
            stage = "accepted" if ok else "failed"
        else:
            io = IO(
                work=work,
                inp=work / "in",
                out=work / "out",
                fixtures=drill.dir / "fixtures",
                drill=drill.dir,
                lang=lang,
                meta=drill.meta,
            )
            try:
                verifier_failures = load_verifier(drill)(io)
            except Exception:
                verifier_failures = None
            at_verifier = (
                not ok
                and verifier_failures is not None
                and problems == list(verifier_failures)
            )
            intended_defect = at_verifier and any(expected in p for p in problems)
            accepted = bool(intended_defect)
            stage = "verifier-rejected" if accepted else "wrong-stage-or-accepted"
        return {
            "path": path.relative_to(drill.dir).as_posix(),
            "language": lang,
            "passed": accepted,
            "stage": stage,
            "elapsed_ms": round(elapsed),
            "problems": problems,
        }
    finally:
        shutil.rmtree(work, ignore_errors=True)


def calibrate(drill, timeout: float) -> dict:
    lineage, fixture_origin, controls = read_controls(drill.dir)
    if not drill.solutions:
        raise ValueError(f"{drill.id}: no reference solutions")
    results = [
        run_case(drill, path, lang, timeout, expected=None)
        for lang, path in sorted(drill.solutions.items())
    ]
    for control in controls:
        path = (drill.dir / control["path"]).resolve()
        lang = path.suffix.lstrip(".").lower()
        if lang not in drill.solutions:
            raise ValueError(f"{drill.id}: control language {lang!r} has no reference")
        result = run_case(drill, path, lang, timeout, expected=control["expect"])
        result["defect"] = control["defect"]
        result["expected_diagnostic"] = control["expect"]
        results.append(result)
    return {
        "drill": drill.id,
        "lineage": lineage,
        "fixture_origin": fixture_origin,
        "stage": "reference-calibrated" if all(r["passed"] for r in results) else "authored",
        "sources": source_hashes(drill.dir),
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("drill", help="drill ID to calibrate")
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--out", type=Path, help="write JSON evidence to this path")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    ids = {drill.id: drill for drill in discover()}
    if args.drill not in ids:
        parser.error(f"unknown drill {args.drill!r}")
    try:
        report = calibrate(ids[args.drill], args.timeout)
    except (OSError, ValueError) as exc:
        print(f"calibration failed: {exc}", file=sys.stderr)
        return 2
    report["calibrated_at"] = datetime.now(timezone.utc).isoformat()
    report["contract"] = "scriptdeck.calibration.v1"
    for result in report["results"]:
        label = "PASS" if result["passed"] else "FAIL"
        print(f"{label} {report['drill']} {result['path']} ({result['stage']})")
        if not result["passed"]:
            for problem in result["problems"]:
                print(f"  {problem}")
    print(f"stage: {report['stage']}")
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"evidence: {args.out}")
    return 0 if report["stage"] == "reference-calibrated" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""scriptdeck harness — scaffold, list, and run scripting drills.

    python3 harness/run.py list
    python3 harness/run.py run 001-csv-rollup
    python3 harness/run.py run all --lang python,bash --timeout 30
    python3 harness/run.py new 007-slug

Each solution runs in a throwaway directory with this contract:

    <work>/in/   fixtures, copied in
    <work>/out/  where the solution writes its answers
    $IN $OUT $WORK  the same paths, absolute
    $API_BASE   set when the drill declares a mock_server

A drill may ship a `setup.py` (or `setup.sh`) that runs first, with $IN pointing at the
copied fixtures — use it for inputs that cannot be committed as text (UTF-16, gzip,
binary junk).

Exit status is 0 only when every selected drill/language pair passes.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRILLS = ROOT / "drills"
HARNESS_DIR = Path(__file__).resolve().parent

# suffix -> interpreter argv. Language label is the suffix itself.
INTERPRETERS: dict[str, list[str]] = {
    "bash": ["bash"],
    "sh": ["bash"],
    "zsh": ["zsh"],
    "py": [sys.executable],
    "lua": ["lua"],
    "js": ["node"],
    "rb": ["ruby"],
    "pl": ["perl"],
    "tcl": ["tclsh"],
    "jxa": ["osascript", "-l", "JavaScript"],
    "ps1": ["pwsh", "-NoProfile", "-NonInteractive", "-File"],
}

REQUIRED: dict[str, type] = {
    "id": str,
    "family": str,
    "title": str,
    "difficulty": int,
    "timebox": int,
    "teaches": list,
}

FAMILIES = {
    "data-wrangling",
    "api-probing",
    "web-scraping",
    "file-hygiene",
    "text-munging",
    "system-recon",
    "network-recon",
}


@dataclass
class Drill:
    dir: Path
    meta: dict
    solutions: dict[str, Path] = field(default_factory=dict)

    @property
    def id(self) -> str:
        return self.meta["id"]

    @property
    def langs(self) -> list[str]:
        return sorted(self.solutions)

    @property
    def track(self) -> str:
        """Sub-track directory (data/, clean/, ops/, apply/), or '-' for a flat drill."""
        try:
            relative = self.dir.parent.relative_to(DRILLS).as_posix()
        except ValueError:
            return "-"
        return relative if relative != "." else "-"


@dataclass
class IO:
    """Handed to each drill's verify.py. Read it, do not mutate the tree."""

    work: Path
    inp: Path
    out: Path
    fixtures: Path
    drill: Path
    lang: str
    meta: dict


# --------------------------------------------------------------------------- load


def load_drill(path: Path) -> Drill:
    toml = path / "drill.toml"
    if not toml.is_file():
        raise SystemExit(f"{path}: missing drill.toml")
    meta = tomllib.loads(toml.read_text(encoding="utf-8"))
    for key, want in REQUIRED.items():
        if key not in meta:
            raise SystemExit(f"{toml}: missing required key {key!r}")
        if not isinstance(meta[key], want):
            raise SystemExit(f"{toml}: {key!r} must be {want.__name__}")
    if meta["family"] not in FAMILIES:
        raise SystemExit(f"{toml}: family {meta['family']!r} not in {sorted(FAMILIES)}")
    if path.name != meta["id"]:
        raise SystemExit(f"{path}: id {meta['id']!r} must match directory name")

    solutions: dict[str, Path] = {}
    sdir = path / "solutions"
    if sdir.is_dir():
        for f in sorted(sdir.iterdir()):
            if not f.is_file() or f.name.startswith("."):
                continue
            suffix = f.suffix.lstrip(".").lower()
            if suffix not in INTERPRETERS:
                continue
            solutions[suffix] = f
    return Drill(path, meta, solutions)


def discover() -> list[Drill]:
    if not DRILLS.is_dir():
        raise SystemExit(f"no drills/ directory at {DRILLS}")
    found = [load_drill(path.parent) for path in sorted(DRILLS.rglob("drill.toml"))]
    if not found:
        raise SystemExit("no drills found")
    return sorted(found, key=lambda drill: drill.id)


# --------------------------------------------------------------------------- mock


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def free_port_in_range(low: int, high: int) -> int:
    for port in range(low, high + 1):
        with socket.socket() as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port
    raise SystemExit(f"no free port in range {low}-{high}")


def kill_listener(out: Path) -> None:
    """Stop a service the solution started, using the pid file it wrote."""
    pid_file = out / "listener.pid"
    if not pid_file.is_file():
        return
    try:
        pid = int(pid_file.read_text(encoding="utf-8").strip())
    except (ValueError, OSError):
        return
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.kill(pid, sig)
        except (ProcessLookupError, PermissionError):
            return
        time.sleep(0.2)
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return


def wait_port(port: int, deadline: float = 5.0) -> bool:
    start = time.monotonic()
    while time.monotonic() - start < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.25):
                return True
        except OSError:
            time.sleep(0.05)
    return False


def start_mock(drill: Drill, env: dict[str, str]) -> subprocess.Popen | None:
    rel = (drill.meta.get("mock_server") or "").strip()
    if not rel:
        return None
    script = drill.dir / rel
    if not script.is_file():
        raise SystemExit(f"{drill.id}: mock_server not found: {rel}")
    port = free_port()
    rng = drill.meta.get("mock_port_range")
    if rng:
        port = free_port_in_range(int(rng[0]), int(rng[1]))
    env["PORT"] = str(port)
    env["API_BASE"] = f"http://127.0.0.1:{port}"
    proc = subprocess.Popen(
        [sys.executable, str(script)],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    if not wait_port(port):
        proc.terminate()
        raise SystemExit(f"{drill.id}: mock server did not come up on :{port}")
    return proc


# --------------------------------------------------------------------------- verify


def load_verifier(drill: Drill):
    path = drill.dir / "verify.py"
    if not path.is_file():
        raise SystemExit(f"{drill.id}: missing verify.py")
    if str(HARNESS_DIR) not in sys.path:
        sys.path.insert(0, str(HARNESS_DIR))  # so graders can `import verifylib`
    name = "verify_" + drill.id.replace("-", "_")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"{drill.id}: cannot load verify.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fn = getattr(mod, "verify", None)
    if not callable(fn):
        raise SystemExit(f"{drill.id}: verify.py must define verify(io) -> list[str]")
    return fn


# --------------------------------------------------------------------------- run


def run_solution(
    drill: Drill,
    lang: str,
    solution: Path,
    timeout: float,
    keep: bool,
    verbose: bool,
) -> tuple[bool, list[str], float, Path]:
    work = Path(tempfile.mkdtemp(prefix=f"deck-{drill.id}-{lang}-"))
    inp = work / "in"
    out = work / "out"
    fixtures = drill.dir / "fixtures"
    if fixtures.is_dir():
        shutil.copytree(fixtures, inp)
    else:
        inp.mkdir()
    out.mkdir()

    env = os.environ.copy()
    env.update({"IN": str(inp), "OUT": str(out), "WORK": str(work), "NO_COLOR": "1"})

    # Optional setup hook: fixtures that cannot be committed as text (UTF-16, gzip,
    # binary junk) are generated into the work tree before the solution runs.
    setup = drill.dir / "setup.py"
    setup_cmd = [sys.executable, str(setup)] if setup.is_file() else None
    if setup_cmd is None:
        shell_setup = drill.dir / "setup.sh"
        if shell_setup.is_file():
            setup_cmd = ["bash", str(shell_setup)]
    if setup_cmd is not None:
        try:
            proc = subprocess.run(
                setup_cmd, cwd=work, env=env, capture_output=True, text=True, timeout=timeout
            )
        except subprocess.TimeoutExpired:
            return False, ["setup script timed out"], 0.0, work
        if proc.returncode != 0:
            detail = (proc.stderr or proc.stdout).strip().splitlines()[-5:]
            return False, [f"setup script failed (exit {proc.returncode})"] + [
                f"  {line}" for line in detail
            ], 0.0, work

    # Optional probe: the solution may start a service (a listener) that the probe
    # then talks to. The port is allocated up front so the solution knows where to bind.
    probe = drill.dir / "probe.py"
    if probe.is_file():
        probe_port = free_port()
        env["PORT"] = str(probe_port)
        env["API_BASE"] = f"http://127.0.0.1:{probe_port}"

    mock = start_mock(drill, env)
    argv = INTERPRETERS[lang] + [str(solution)]
    started = time.monotonic()
    try:
        proc = subprocess.run(
            argv,
            cwd=work,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        elapsed = (time.monotonic() - started) * 1000
        return False, [f"timed out after {timeout:.0f}s"], elapsed, work
    finally:
        if mock is not None:
            mock.terminate()
            try:
                mock.wait(timeout=2)
            except subprocess.TimeoutExpired:
                mock.kill()

    elapsed = (time.monotonic() - started) * 1000

    if verbose:
        if proc.stdout.strip():
            print(indent(proc.stdout.rstrip(), "      stdout | "))
        if proc.stderr.strip():
            print(indent(proc.stderr.rstrip(), "      stderr | "))

    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout).strip().splitlines()[-6:]
        return False, [f"exit {proc.returncode}"] + [f"  {line}" for line in tail], elapsed, work

    io = IO(
        work=work, inp=inp, out=out, fixtures=fixtures, drill=drill.dir, lang=lang, meta=drill.meta
    )
    if probe.is_file():
        try:
            probe_proc = subprocess.run(
                [sys.executable, str(probe)],
                cwd=work,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            probe_proc = None
        finally:
            kill_listener(out)
        if probe_proc is None:
            return False, ["probe timed out"], elapsed, work
        if probe_proc.returncode != 0:
            detail = (probe_proc.stderr or probe_proc.stdout).strip().splitlines()[-5:]
            return False, [f"probe failed (exit {probe_proc.returncode})"] + [
                f"  {line}" for line in detail
            ], elapsed, work
    try:
        failures = load_verifier(drill)(io)
    except Exception as exc:  # a broken grader is a failure, not a crash
        failures = [f"verifier raised {type(exc).__name__}: {exc}"]
    if failures is None:
        failures = []
    return not failures, list(failures), elapsed, work


def indent(text: str, prefix: str) -> str:
    return "\n".join(prefix + line for line in text.splitlines())


def cmd_run(args: argparse.Namespace) -> int:
    drills = discover()
    wanted = args.target
    if wanted != "all":
        ids = {d.id: d for d in drills}
        if wanted not in ids:
            print(f"unknown drill {wanted!r}. known: {', '.join(sorted(ids))}", file=sys.stderr)
            return 2
        drills = [ids[wanted]]

    only = {s.strip().lstrip(".") for s in (args.lang or "").split(",") if s.strip()}
    checks = passed = 0

    for drill in drills:
        langs = [lang for lang in drill.langs if not only or lang in only]
        if not langs:
            print(f"{drill.id:<28} {'':>8}  SKIP  (no solution for {sorted(only) or 'any language'})")
            continue
        for lang in langs:
            if lang == "jxa" and sys.platform != "darwin":
                print(f"{drill.id:<28} {lang:>8}  SKIP  (JXA requires macOS)")
                continue
            ok, problems, elapsed, work = run_solution(
                drill, lang, drill.solutions[lang], args.timeout, args.keep, args.verbose
            )
            checks += 1
            status = "PASS" if ok else "FAIL"
            passed += ok
            print(f"{drill.id:<28} {lang:>8}  {status}  {elapsed:6.0f}ms")
            if not ok:
                for problem in problems:
                    print(f"      - {problem}")
            if args.keep:
                print(f"      work: {work}")
            else:
                shutil.rmtree(work, ignore_errors=True)

    print(f"\n{passed}/{checks} passed")
    return 0 if passed == checks and checks else 1


def cmd_list(_: argparse.Namespace) -> int:
    drills = discover()
    print(f"{'id':<28} {'track':<8} {'family':<16} {'d':>2} {'timebox':>8}  languages")
    for d in drills:
        print(
            f"{d.id:<28} {d.track:<8} {d.meta['family']:<16} {d.meta['difficulty']:>2} "
            f"{d.meta['timebox']:>7}s  {', '.join(d.langs) or '(none)'}"
        )
    print(f"\n{len(drills)} drills")
    return 0


SCAFFOLD_VERIFY = '''\"\"\"Grader for {id}. Return [] on success, or a list of human-readable failures.\"\"\"


def verify(io):
    failures = []
    # out = io.out / "answer.csv"
    # if not out.is_file():
    #     return ["missing out/answer.csv"]
    # rows = out.read_text().splitlines()
    # if len(rows) != 4:
    #     failures.append(f"expected 4 rows, got {{len(rows)}}")
    return failures
'''

SCAFFOLD_TOML = '''id = "{id}"
family = "{family}"
title = "{title}"
difficulty = 1
timebox = 180
teaches = ["fill this in"]
'''

SCAFFOLD_PROMPT = '''# {id}

## Task

One paragraph: what question are we answering, in the voice of a colleague asking
for it, not a spec.

## Input

`in/` contains ...

## Output

Write exactly these files to `$OUT`:

- `out/...` - description, order, format

## Messes to expect

- ...

## Timebox

A few minutes. If you are past that, the approach is wrong.
'''


def cmd_new(args: argparse.Namespace) -> int:
    slug = args.id
    if not slug or "/" in slug or " " in slug:
        print("id must be a slug like 007-my-drill", file=sys.stderr)
        return 2
    path = DRILLS / slug
    if path.exists():
        print(f"{path} already exists", file=sys.stderr)
        return 2
    (path / "fixtures").mkdir(parents=True)
    (path / "solutions").mkdir()
    (path / "fixtures" / ".gitkeep").write_text("")
    (path / "drill.toml").write_text(
        SCAFFOLD_TOML.format(id=slug, family=args.family, title=args.title)
    )
    (path / "PROMPT.md").write_text(SCAFFOLD_PROMPT.format(id=slug))
    (path / "verify.py").write_text(SCAFFOLD_VERIFY.format(id=slug))
    print(f"scaffolded {path.relative_to(ROOT)}")
    print("next:")
    print(f"  1. write {slug}/PROMPT.md and fixtures/")
    print(f"  2. write {slug}/solutions/solve.py")
    print(f"  3. write {slug}/verify.py")
    print(f"  4. python3 harness/run.py run {slug}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="run.py", description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="run a drill (or 'all')")
    r.add_argument("target", help="drill id, or 'all'")
    r.add_argument("--lang", help="comma-separated suffixes to run, e.g. python,bash")
    r.add_argument("--timeout", type=float, default=60.0, help="per-solution seconds (default 60)")
    r.add_argument("--keep", action="store_true", help="keep work dirs and print their paths")
    r.add_argument("-v", "--verbose", action="store_true", help="show solution stdout/stderr")
    r.set_defaults(fn=cmd_run)

    lst = sub.add_parser("list", help="list drills")
    lst.set_defaults(fn=cmd_list)

    n = sub.add_parser("new", help="scaffold a drill")
    n.add_argument("id")
    n.add_argument("--family", default="data-wrangling", choices=sorted(FAMILIES))
    n.add_argument("--title", default="untitled")
    n.set_defaults(fn=cmd_new)

    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())

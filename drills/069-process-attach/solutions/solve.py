#!/usr/bin/env python3
"""Start a child, attach through its PID, sample it, and clean it up."""

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

root = Path(os.environ["IN"])
work = Path(os.environ["WORK"])
out = Path(os.environ["OUT"])
ready = work / "ready.json"
stop = work / "stop.flag"
heartbeat = work / "heartbeat.txt"
child = subprocess.Popen(
    [sys.executable, str(root / "worker.py"), str(ready), str(stop), str(heartbeat)],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

try:
    deadline = time.monotonic() + 5
    while not ready.is_file() and time.monotonic() < deadline:
        if child.poll() is not None:
            raise SystemExit("worker exited before ready")
        time.sleep(0.05)
    if not ready.is_file():
        raise SystemExit("worker readiness timed out")
    ready_pid = int(json.loads(ready.read_text(encoding="utf-8"))["pid"])
    if ready_pid != child.pid:
        raise SystemExit("worker PID mismatch")
    port = int(json.loads(ready.read_text(encoding="utf-8"))["port"])
    if child.poll() is not None:
        raise SystemExit(f"cannot attach to PID {ready_pid}")
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2) as response:
        listener_ok = response.status == 200 and response.read().decode().strip() == "ready"
    if not listener_ok:
        raise SystemExit(f"listener probe failed on port {port}")
    before = int(heartbeat.read_text(encoding="utf-8"))
    time.sleep(0.12)
    after = int(heartbeat.read_text(encoding="utf-8"))
    if after <= before:
        raise SystemExit("heartbeat did not advance")
finally:
    stop.write_text("stop\n", encoding="utf-8")
    try:
        child.wait(timeout=2)
    except subprocess.TimeoutExpired:
        child.terminate()
        child.wait(timeout=2)

if child.poll() is None:
    raise SystemExit("worker still running")
(out / "attachment.json").write_text(
    json.dumps({
        "pid": child.pid,
        "ready_pid": ready_pid,
        "port": port,
        "heartbeat_before": before,
        "heartbeat_after": after,
        "attached": True,
        "listener_ok": True,
        "stopped": True,
    }) + "\n",
    encoding="utf-8",
)

"""Grader for 054-listener-setup."""

import json


def verify(io):
    probe = io.out / "probe.json"
    if not probe.is_file():
        return ["probe.json missing — the probe never ran"]

    try:
        data = json.loads(probe.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"probe.json is not valid JSON: {exc}"]

    failures = []
    if data.get("status") != 200:
        failures.append(
            f"listener answered status {data.get('status')!r}, expected 200 "
            f"(probe error: {data.get('error', '')})"
        )
    if data.get("body") != "hello scriptdeck":
        failures.append(f"listener body: expected 'hello scriptdeck', got {data.get('body')!r}")

    pid_file = io.out / "listener.pid"
    if not pid_file.is_file():
        failures.append("missing out/listener.pid")
    else:
        raw = pid_file.read_text(encoding="utf-8").strip()
        if not raw.isdigit():
            failures.append(f"out/listener.pid should hold a pid, got {raw!r}")

    return failures

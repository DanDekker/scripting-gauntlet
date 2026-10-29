"""Grader for 069-process-attach."""

import json


def verify(io):
    path = io.out / "attachment.json"
    if not path.is_file():
        return ["missing attachment.json"]
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"attachment.json is invalid: {exc}"]
    want = {"pid", "ready_pid", "port", "heartbeat_before", "heartbeat_after", "attached", "listener_ok", "stopped"}
    failures = []
    if set(result) != want:
        failures.append(f"attachment.json keys: expected {sorted(want)}, got {sorted(result)}")
        return failures
    if not isinstance(result["pid"], int) or result["pid"] <= 0 or result["ready_pid"] != result["pid"]:
        failures.append("PID from ready file must match the launched child PID")
    if not isinstance(result["port"], int) or not 1 <= result["port"] <= 65535:
        failures.append("listener port is invalid")
    if not isinstance(result["heartbeat_before"], int) or result["heartbeat_after"] <= result["heartbeat_before"]:
        failures.append("heartbeat did not advance while attached")
    if result["attached"] is not True:
        failures.append("child process was not found by PID")
    if result["listener_ok"] is not True:
        failures.append("listener health probe failed")
    if result["stopped"] is not True:
        failures.append("child process was still running after cleanup")
    return failures

"""Independent semantic checks for the synthetic macOS plist fixture."""

import json

EXPECTED = [
    {"id": "com.example.capture", "version": "2.4.1", "permissions": ["camera", "microphone"]},
    {"id": "com.example.mic", "version": "0.9", "permissions": ["microphone"]},
    {"id": "com.example.trim", "version": "3.2", "permissions": ["camera"]},
]


def verify(io):
    report = io.out / "report.json"
    if not report.is_file():
        return ["missing out/report.json"]
    try:
        data = json.loads(report.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"report.json is not valid JSON: {exc}"]
    if not isinstance(data, dict) or set(data) != {"apps", "skipped"}:
        return ["report.json must have exactly apps and skipped"]
    failures = []
    if type(data["skipped"]) is not int or data["skipped"] != 2:
        failures.append(f"skipped: expected 2, got {data['skipped']!r}")
    apps = data["apps"]
    if not isinstance(apps, list):
        return failures + ["apps must be an array"]
    if [app.get("id") for app in apps if isinstance(app, dict)] != [app["id"] for app in EXPECTED]:
        return failures + ["apps: expected the selected bundle IDs in ascending order"]
    for actual, expected in zip(apps, EXPECTED):
        if not isinstance(actual, dict) or set(actual) != {"id", "version", "permissions"}:
            failures.append("each app needs exactly id, version, and permissions")
            continue
        if actual["version"] != expected["version"]:
            failures.append(f"{actual['id']}: wrong version")
        if actual["permissions"] != expected["permissions"]:
            failures.append(f"{actual['id']}: permissions must match both nonblank declarations")
    return failures

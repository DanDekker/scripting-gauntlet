"""Grader for 236-perl-auth-fail2ban. Return [] on success, or a list of human-readable failures."""

import json


def verify(io):
    failures = []

    bans_file = io.out / "bans.tsv"
    if not bans_file.is_file():
        return ["missing out/bans.tsv"]

    expected_rows = [
        ["ip", "failures", "unique_users", "users"],
        ["192.168.2.200", "5", "4", "admin,guest,root,test"],
        ["192.168.1.50", "4", "3", "admin,deployer,root"],
        ["10.0.0.25", "3", "2", "oracle,postgres"],
    ]

    lines = [line for line in bans_file.read_text(encoding="utf-8").splitlines() if line]
    if len(lines) != len(expected_rows):
        failures.append(f"expected {len(expected_rows)} lines in out/bans.tsv, got {len(lines)}")
    else:
        for idx, (actual_line, exp) in enumerate(zip(lines, expected_rows)):
            parts = actual_line.split("\t")
            if parts != exp:
                failures.append(f"row {idx}: expected {exp!r}, got {parts!r}")

    summary_file = io.out / "summary.json"
    if not summary_file.is_file():
        failures.append("missing out/summary.json")
    else:
        try:
            data = json.loads(summary_file.read_text(encoding="utf-8"))
            if data.get("total_failed_events") != 15:
                failures.append(f"expected total_failed_events=15, got {data.get('total_failed_events')}")
            if data.get("unique_ips") != 5:
                failures.append(f"expected unique_ips=5, got {data.get('unique_ips')}")
            if data.get("banned_ips") != 3:
                failures.append(f"expected banned_ips=3, got {data.get('banned_ips')}")
            if data.get("top_target_user") != "root":
                failures.append(f"expected top_target_user='root', got {data.get('top_target_user')!r}")
        except Exception as e:
            failures.append(f"invalid JSON in out/summary.json: {e}")

    return failures


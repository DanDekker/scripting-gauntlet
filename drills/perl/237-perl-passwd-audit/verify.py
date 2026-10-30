"""Grader for 237-perl-passwd-audit. Return [] on success, or a list of human-readable failures."""

import json


def verify(io):
    failures = []

    tsv_file = io.out / "anomalies.tsv"
    if not tsv_file.is_file():
        return ["missing out/anomalies.tsv"]

    expected_rows = [
        ["category", "entity", "detail"],
        ["DANGLING_MEMBER", "group:docker", "member mallory not found in passwd database"],
        ["DANGLING_MEMBER", "group:wheel", "member dave not found in passwd database"],
        ["DUPLICATE_UID", "user:alice", "uid 1001 is duplicated"],
        ["DUPLICATE_UID", "user:bob", "uid 1001 is duplicated"],
        ["DUPLICATE_UID", "user:root", "uid 0 is duplicated"],
        ["DUPLICATE_UID", "user:toor", "uid 0 is duplicated"],
        ["ORPHAN_GID", "user:ghost", "gid 9999 not found in group database"],
        ["ROOT_EQUIV", "user:toor", "uid 0 assigned to non-root user"],
    ]

    lines = [line for line in tsv_file.read_text(encoding="utf-8").splitlines() if line]
    if len(lines) != len(expected_rows):
        failures.append(f"expected {len(expected_rows)} lines in out/anomalies.tsv, got {len(lines)}")
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
            if data.get("total_users") != 10:
                failures.append(f"expected total_users=10, got {data.get('total_users')}")
            if data.get("total_groups") != 10:
                failures.append(f"expected total_groups=10, got {data.get('total_groups')}")
            if data.get("total_anomalies") != 8:
                failures.append(f"expected total_anomalies=8, got {data.get('total_anomalies')}")
            if data.get("root_equiv_users") != 1:
                failures.append(f"expected root_equiv_users=1, got {data.get('root_equiv_users')}")
            if data.get("orphan_gid_users") != 1:
                failures.append(f"expected orphan_gid_users=1, got {data.get('orphan_gid_users')}")
            if data.get("dangling_members") != 2:
                failures.append(f"expected dangling_members=2, got {data.get('dangling_members')}")
        except Exception as e:
            failures.append(f"invalid JSON in out/summary.json: {e}")

    return failures


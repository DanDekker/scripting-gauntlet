#!/usr/bin/env python3
import json
from pathlib import Path

passwd_path = Path("in/passwd")
group_path = Path("in/group")

users: dict[str, dict] = {}
uid_counts: dict[int, int] = {}

for line in passwd_path.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    fields = line.split(":")
    if len(fields) != 7:
        continue
    username, pwd, uid_str, gid_str, gecos, home, shell = fields
    uid = int(uid_str)
    gid = int(gid_str)
    users[username] = {"uid": uid, "gid": gid}
    uid_counts[uid] = uid_counts.get(uid, 0) + 1

groups: dict[int, str] = {}
group_names: list[str] = []
group_members: dict[str, list[str]] = {}

for line in group_path.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    fields = line.split(":")
    if len(fields) != 4:
        continue
    groupname, pwd, gid_str, members_str = fields
    gid = int(gid_str)
    groups[gid] = groupname
    group_names.append(groupname)
    members = [m for m in members_str.split(",") if m]
    group_members[groupname] = members

anomalies = []
root_equiv_count = 0
orphan_gid_count = 0
dangling_count = 0

for user in sorted(users.keys()):
    uid = users[user]["uid"]
    gid = users[user]["gid"]

    if uid == 0 and user != "root":
        anomalies.append({
            "category": "ROOT_EQUIV",
            "entity": f"user:{user}",
            "detail": "uid 0 assigned to non-root user",
        })
        root_equiv_count += 1

    if uid_counts[uid] > 1:
        anomalies.append({
            "category": "DUPLICATE_UID",
            "entity": f"user:{user}",
            "detail": f"uid {uid} is duplicated",
        })

    if gid not in groups:
        anomalies.append({
            "category": "ORPHAN_GID",
            "entity": f"user:{user}",
            "detail": f"gid {gid} not found in group database",
        })
        orphan_gid_count += 1

for group in sorted(group_members.keys()):
    for member in group_members[group]:
        if member not in users:
            anomalies.append({
                "category": "DANGLING_MEMBER",
                "entity": f"group:{group}",
                "detail": f"member {member} not found in passwd database",
            })
            dangling_count += 1

anomalies.sort(key=lambda x: (x["category"], x["entity"], x["detail"]))

out_dir = Path("out")
out_dir.mkdir(parents=True, exist_ok=True)

tsv_lines = ["category\tentity\tdetail"]
for a in anomalies:
    tsv_lines.append(f"{a['category']}\t{a['entity']}\t{a['detail']}")
Path("out/anomalies.tsv").write_text("\n".join(tsv_lines) + "\n", encoding="utf-8")

summary = {
    "dangling_members": dangling_count,
    "orphan_gid_users": orphan_gid_count,
    "root_equiv_users": root_equiv_count,
    "total_anomalies": len(anomalies),
    "total_groups": len(group_names),
    "total_users": len(users),
}

Path("out/summary.json").write_text(json.dumps(summary, separators=(",", ":")), encoding="utf-8")

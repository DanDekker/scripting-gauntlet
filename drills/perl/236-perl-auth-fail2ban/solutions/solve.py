#!/usr/bin/env python3
import json
import re
from pathlib import Path

in_path = Path("in/auth.log")
lines = in_path.read_text(encoding="utf-8").splitlines()

pattern = re.compile(r"Failed password for (?:invalid user )?(\S+) from (\S+) port (\d+)")

ip_failures: dict[str, int] = {}
ip_users: dict[str, set[str]] = {}
user_counts: dict[str, int] = {}
total_failed = 0

for line in lines:
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    m = pattern.search(line)
    if m:
        user, ip, _port = m.groups()
        total_failed += 1
        ip_failures[ip] = ip_failures.get(ip, 0) + 1
        ip_users.setdefault(ip, set()).add(user)
        user_counts[user] = user_counts.get(user, 0) + 1

out_dir = Path("out")
out_dir.mkdir(parents=True, exist_ok=True)

banned = [ip for ip, count in ip_failures.items() if count >= 3]
banned.sort(key=lambda ip: (-ip_failures[ip], ip))

tsv_lines = ["ip\tfailures\tunique_users\tusers"]
for ip in banned:
    users_sorted = sorted(ip_users[ip])
    tsv_lines.append(f"{ip}\t{ip_failures[ip]}\t{len(users_sorted)}\t{','.join(users_sorted)}")

Path("out/bans.tsv").write_text("\n".join(tsv_lines) + "\n", encoding="utf-8")

top_user = sorted(user_counts.keys(), key=lambda u: (-user_counts[u], u))[0] if user_counts else ""

summary = {
    "banned_ips": len(banned),
    "top_target_user": top_user,
    "total_failed_events": total_failed,
    "unique_ips": len(ip_failures),
}

Path("out/summary.json").write_text(json.dumps(summary, separators=(",", ":")), encoding="utf-8")

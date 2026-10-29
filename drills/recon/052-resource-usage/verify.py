"""Grader for 052-resource-usage.

Hand-read off the fixtures: the longest mount point containing /var/lib/app/queue.db is
/var/lib/app (61%, 81788928 KB available), /var is 97% and /var/lib/appdata is a decoy.
uptime has load1 3.42 with 8 CPUs, so load_per_cpu is 0.43 and warning is false.
"""

import verifylib

EXPECTED = {
    "path": "/var/lib/app/queue.db",
    "mount": "/var/lib/app",
    "used_pct": 61,
    "available_kb": 81788928,
    "load1": 3.42,
    "cpus": 8,
    "load_per_cpu": 0.43,
    "warning": False,
    "mounts": 8,
}


def verify(io):
    return verifylib.json_eq(io.out / "resources.json", EXPECTED)

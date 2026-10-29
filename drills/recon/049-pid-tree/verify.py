"""Grader for 049-pid-tree.

Depths, descendants and orphans were walked by hand from fixtures/ps-snapshot.txt
(22 rows: 3 depth-0 roots, max depth 4). The grader restates the contract from
PROMPT.md; it does not recompute the tree.
"""

import verifylib

# depth asc, then pid asc (numeric).
TREE = [
    (1, 0, 0, "/sbin/launchd"),
    (550, 499, 0, "/usr/bin/log stream --style compact"),
    (602, 2, 0, "[kworker/1:2]"),
    (42, 1, 1, "/usr/sbin/syslogd"),
    (57, 1, 1, "/usr/libexec/UserEventAgent"),
    (205, 1, 1, "/Applications/Safari.app/Contents/MacOS/Safari"),
    (301, 1, 1, "/usr/sbin/cfprefsd daemon"),
    (388, 1, 1, "node <defunct>"),
    (501, 1, 1, "/usr/bin/mds_stores"),
    (502, 1, 1, "/usr/libexec/taskgated -s"),
    (601, 1, 1, "[kworker/0:1]"),
    (101, 42, 2, "/usr/bin/sshd -D"),
    (206, 205, 2, "/Applications/Safari.app/Contents/MacOS/Safari"),
    (207, 205, 2, "/usr/libexec/SafariCloudHistoryPushAgent"),
    (412, 388, 2, "/opt/homebrew/bin/node /srv/api/server.js"),
    (102, 101, 3, "python3 /opt/agent/collector.py --interval 30"),
    (103, 101, 3, "python3 /opt/agent/collector.py --interval 120"),
    (104, 101, 3, "bash /opt/agent/run.sh"),
    (208, 206, 3, "/usr/libexec/SafariNotificationAgent"),
    (413, 412, 3, "node /srv/api/worker.js"),
    (414, 412, 3, "node /srv/api/worker.js"),
    (209, 208, 4, "/usr/bin/curl https://example.com/feed"),
]

ORPHANS = [
    (550, 499, "/usr/bin/log stream --style compact"),
    (602, 2, "[kworker/1:2]"),
]

DESCENDANTS = ["206", "207", "208", "209"]

SUMMARY = {"processes": 22, "roots": 3, "max_depth": 4}


def verify(io):
    failures = verifylib.table(io.out / "tree.csv", ["pid", "ppid", "depth", "command"], TREE)
    failures += verifylib.table(io.out / "orphans.csv", ["pid", "ppid", "command"], ORPHANS)
    failures += verifylib.lines(io.out / "descendants.txt", DESCENDANTS)
    failures += verifylib.json_eq(io.out / "summary.json", SUMMARY)
    return failures

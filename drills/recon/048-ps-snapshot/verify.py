"""Grader for 048-ps-snapshot.

Every expected value below was counted by hand from fixtures/ps-snapshot.txt (22 process
rows, 17 distinct executables, 164984 KB resident) and cross-checked against both
solutions. The grader states the contract from PROMPT.md; it does not re-derive it.
"""

import verifylib

TOP_RSS = [
    (205, 1, 22088, 3.8, "/Applications/Safari.app/Contents/MacOS/Safari"),
    (501, 1, 20480, 5.2, "/usr/bin/mds_stores"),
    (102, 101, 15320, 2.7, "python3 /opt/agent/collector.py --interval 30"),
    (103, 101, 15320, 0.9, "python3 /opt/agent/collector.py --interval 120"),
    (502, 1, 15320, 0.3, "/usr/libexec/taskgated -s"),
]

# processes desc, then command asc (bytes)
COMMANDS = [
    ("node", 4),
    ("Safari", 2),
    ("python3", 2),
    ("SafariCloudHistoryPushAgent", 1),
    ("SafariNotificationAgent", 1),
    ("UserEventAgent", 1),
    ("[kworker/0:1]", 1),
    ("[kworker/1:2]", 1),
    ("bash", 1),
    ("cfprefsd", 1),
    ("curl", 1),
    ("launchd", 1),
    ("log", 1),
    ("mds_stores", 1),
    ("sshd", 1),
    ("syslogd", 1),
    ("taskgated", 1),
]

SUMMARY = {"processes": 22, "total_rss_kb": 164984, "commands": 17}


def verify(io):
    failures = verifylib.table(
        io.out / "top_rss.csv",
        ["pid", "ppid", "rss_kb", "cpu", "command"],
        TOP_RSS,
    )
    failures += verifylib.table(io.out / "commands.csv", ["command", "processes"], COMMANDS)
    failures += verifylib.json_eq(io.out / "summary.json", SUMMARY)
    return failures

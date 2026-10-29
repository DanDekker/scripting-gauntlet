"""Grader for 042-replace-text."""

import verifylib

TREE = {
    "README.txt": (
        "Service docs used to live at https://api.example.com/docs.\n"
        "They are at https://api.example.com/docs for now.\n"
    ),
    "etc/app.conf": (
        "upstream api.example.com:8443;\n"
        "backup   api.example.com:8444;\n"
        "upstream_api = api.example.com\n"
    ),
    "etc/decoy.conf": "a = apiXexample.com\nb = api.example.com\nc = apiXexample.com\n",
    "etc/edge.conf": "# decoy: apiXexample.com must survive\nupstream api.example.com;\n",
    "etc/notes.md": "nothing to do here\n",
    "site/about.md": "Contact: ops@api.example.com\n",
    "site/index.md": (
        "# Status\n\n"
        "Endpoint: https://api.example.com/v1/status\n"
        "Fallback: https://api.example.com/v1/status?alt=1\n\n"
        "Old host: api.example.com\n"
    ),
}

EXPECTED = {path: text.replace("api.example.com", "api.internal") for path, text in TREE.items()}


def verify(io):
    failures = []
    tree = io.out / "tree"
    for path, want in EXPECTED.items():
        got_path = tree / path
        if not got_path.is_file():
            failures.append(f"missing tree/{path}")
            continue
        got = got_path.read_text(encoding="utf-8")
        if got != want:
            failures.append(
                f"tree/{path}: expected {want!r}, got {got!r}"
            )

    failures += verifylib.lines(
        io.out / "changed.txt",
        [
            "README.txt",
            "etc/app.conf",
            "etc/decoy.conf",
            "etc/edge.conf",
            "site/about.md",
            "site/index.md",
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"files_scanned": 7, "files_changed": 6, "replacements": 11},
    )
    return failures

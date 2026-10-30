"""Grader for 259-tcl-safe-subst."""

from pathlib import Path


EXPECTED = "Name: Ada\nPath: /tmp/demo\nCommand: [clock seconds]\n"


def verify(io):
    path = io.out / "rendered.txt"
    if not path.is_file():
        return ["missing rendered.txt"]
    actual = path.read_text(encoding="utf-8")
    return [] if actual == EXPECTED else [f"rendered.txt: expected inert command text, got {actual!r}"]

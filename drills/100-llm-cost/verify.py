"""Grader for 100-llm-cost."""

import re

import verifylib

MONEY = re.compile(r"^-?\d+\.\d{6}$")
DECIMAL = re.compile(r"-?\d+\.\d+")
COSTS_HEADER = ["request_id", "model", "cost"]
EXPECTED_ROWS = [
    ("r01", "small", 0.036),
    ("r02", "medium", 0.6),
    ("r03", "large", 7.5),
    ("r04", "small", 0.0075),
    ("r06", "medium", 0.15),
    ("r06", "small", 0.036),
    ("r08", "small", 0.009615),
]
EXPECTED_SUMMARY = {
    "requests": 9,
    "priced": 7,
    "unpriced": 2,
    "total_cost": 8.339115,
    "by_model": {"small": 0.089115, "medium": 0.75, "large": 7.5},
}


def _six_decimals(path, label):
    """Every decimal literal in the file must carry exactly 6 decimals."""
    if not path.is_file():
        return [f"missing {label}"]
    text = path.read_text(encoding="utf-8")
    return [
        f"{label}: {token!r} is not 6-decimal money"
        for token in DECIMAL.findall(text)
        if not MONEY.match(token)
    ]


def verify(io) -> list[str]:
    failures = verifylib.table(io.out / "costs.csv", COSTS_HEADER, EXPECTED_ROWS)
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    failures += _six_decimals(io.out / "costs.csv", "costs.csv")
    failures += _six_decimals(io.out / "summary.json", "summary.json")
    return failures

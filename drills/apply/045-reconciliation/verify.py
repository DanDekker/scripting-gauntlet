"""Grader for 045-reconciliation."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "recon.csv",
        ["ref", "ledger_total", "bank_total", "delta", "status"],
        [
            ("INV-1001", 1250.00, 1250.00, 0.00, "matched"),
            ("INV-1002", 300.00, 300.00, 0.00, "matched"),
            ("INV-1003", 99.50, 99.50, 0.00, "matched"),
            ("INV-1004", 820.00, 410.00, 410.00, "amount_mismatch"),
            ("INV-1005", 75.25, 75.30, -0.05, "amount_mismatch"),
            ("INV-1006", 0.00, 1200.00, -1200.00, "missing_in_ledger"),
            ("INV-1007", 80.00, 0.00, 80.00, "missing_in_bank"),
            ("INV-1008", 0.00, -45.00, 45.00, "missing_in_ledger"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "refs": 8,
            "matched": 3,
            "amount_mismatch": 2,
            "missing_in_bank": 1,
            "missing_in_ledger": 2,
            "ledger_total": 2624.75,
            "bank_total": 3289.80,
            "delta": -665.05,
        },
    )
    return failures

"""Grader for 110-license-scan."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "deps.csv",
        ["name", "version", "licence", "status"],
        [
            ("Django", "5.0", "mit", "allowed"),
            ("black", "24.3.0", "apache-2.0", "allowed"),
            ("click", "8.1.7", "bsd-3-clause", "allowed"),
            ("cryptography", "42.0.5", "openssl", "unknown"),
            ("flask", "3.0.1", "bsd-3-clause", "allowed"),
            ("httpx", "0.27.0", "gpl-3.0", "denied"),
            ("loguru", "0.7.2", "agpl-3.0", "denied"),
            ("numpy", "1.26.4", "mit", "allowed"),
            ("pandas", "2.2.0", "psf-2.0", "unknown"),
            ("requests", "2.28.2", "apache-2.0", "allowed"),
            ("requests", "2.31.0", "mit", "allowed"),
            ("requests", "2.31.0", "mit", "allowed"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "deps": 12,
            "skipped": 3,
            "allowed": 8,
            "denied": 2,
            "unknown": 2,
            "conflicts": 1,
        },
    )
    return failures

"""Grader for 080-robots-crawl."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "crawl.csv",
        ["url", "allowed", "rule"],
        [
            ("https://example.com/about", "yes", ""),
            ("https://example.com/admin/public/x", "yes", "/admin/public"),
            ("https://example.com/admin/users", "no", "/admin"),
            ("https://example.com/adminish", "no", "/admin"),
            ("https://example.com/docs/report.pdf", "no", "/*.pdf$"),
            ("https://example.com/docs/report.pdf?v=2", "yes", ""),
            ("https://example.com/private/public/index.html", "yes", ""),
            ("https://example.com/private/secret.html", "yes", ""),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json", {"urls": 8, "allowed": 5, "disallowed": 3}
    )
    return failures

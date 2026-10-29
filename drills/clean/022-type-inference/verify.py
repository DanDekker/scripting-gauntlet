"""Grader for 022-type-inference."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "types.csv",
        ["column", "type"],
        [
            ("row", "integer"),
            ("zip", "string"),
            ("cust_id", "integer"),
            ("qty", "integer"),
            ("ratio", "float"),
            ("hexval", "string"),
            ("special", "string"),
            ("mixed", "string"),
        ],
    )
    failures += verifylib.table(
        io.out / "offenders.csv",
        ["column", "row", "value"],
        [
            ("zip", 1, "02134"),
            ("zip", 3, "00501"),
            ("zip", 4, "01234"),
            ("zip", 5, "00000"),
            ("cust_id", 3, "9007199254740993"),
            ("hexval", 1, "0x10"),
            ("hexval", 2, "0x1f"),
            ("hexval", 3, "0x2a"),
            ("hexval", 4, "0x0"),
            ("hexval", 5, "0xff"),
            ("special", 1, "NaN"),
            ("special", 2, "Infinity"),
            ("mixed", 5, "oops"),
        ],
    )
    return failures

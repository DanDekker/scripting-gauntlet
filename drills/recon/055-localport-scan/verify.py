"""Grader for 055-localport-scan.

The mock records the port it bound to in $WORK/mock.port, so the grader knows exactly
which port a correct scan has to report.
"""

import verifylib


def verify(io):
    port_file = io.work / "mock.port"
    if not port_file.is_file():
        return ["mock.port missing — the mock service never recorded its port"]
    try:
        expected_port = int(port_file.read_text(encoding="utf-8").strip())
    except ValueError:
        return ["mock.port does not contain a port number"]

    failures = []
    rows = verifylib.read_csv(io.out / "open_ports.csv")[1] if (io.out / "open_ports.csv").is_file() else []
    if not (io.out / "open_ports.csv").is_file():
        failures.append("missing out/open_ports.csv")
    else:
        header, rows = verifylib.read_csv(io.out / "open_ports.csv")
        if header != ["port"]:
            failures.append(f"open_ports.csv header: expected ['port'], got {header}")
        else:
            found = []
            for row in rows:
                try:
                    found.append(int(row[0]))
                except ValueError:
                    failures.append(f"open_ports.csv: {row[0]!r} is not a port number")
            if found != [expected_port]:
                failures.append(
                    f"open_ports.csv: expected exactly [{expected_port}], got {found} "
                    "(closed ports must not be reported)"
                )

    failures += verifylib.json_eq(io.out / "summary.json", {"scanned": 11, "open": 1})
    return failures

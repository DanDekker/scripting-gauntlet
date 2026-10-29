# 055-localport-scan

> "Is anything of ours still up on the old ports? Scan the range."

## Task

Scan the loopback interface and report which ports in **46000–46010** (inclusive) are
accepting connections. One service is up; the rest are closed.

## Rules

1. Scan **`127.0.0.1`** only, over TCP. Do not touch other interfaces, and do not scan
   outside the stated range.
2. A port is open if a **TCP connection succeeds**. A refused connection means the port
   is closed — that is the normal answer for most of the range, not an error.
3. Report only the ports that answered, ascending.
4. Count every port you attempted, not just the ones that answered.

## Output

**`out/open_ports.csv`** — header, then one row per open port:

```
port
46003
```

**`out/summary.json`** — exactly two keys: `scanned` (how many ports you attempted) and
`open` (how many answered).

## Messes to expect

- closed ports that refuse instantly — those are successes for the scan, not failures
- a connect that hangs instead of being refused

## Timebox

4 minutes. A refused connect on loopback is immediate; you do not need a long timeout,
but you do need one so a hung port cannot stall the whole range.

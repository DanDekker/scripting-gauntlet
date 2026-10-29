# 131-port-scan-triage

> "I scanned the box and now I have a wall of `open`/`closed`/`filtered`. That is not an
> answer. Cross it against the approved-services sheet and give me the rows I should
> actually look at — plus the full list, so I can see what you decided."

## Input

**`in/scan.txt`** — one probed port per line, straight out of the scanner:

```
22/tcp open ssh 3.14.2
8000-8010/tcp open zmq
```

**`in/baseline.csv`** — the approved-services sheet, header `port,service,expected`:

```
port,service,expected
22,ssh,yes
6379,redis,no
```

- `expected` = `yes` means the port is approved to be **open**, on that service.
- `expected` = `no` means the port is approved to be **closed**.
- A baseline port that was never scanned is ignored.
- A scanned port with no baseline row is **unbaselined**.

## Rules

1. **Line validity.** Fields are the whitespace-separated tokens of the line, numbered from
   1. A line of `scan.txt` is valid when all three hold:
   (a) it has at least two fields — the port field and the state,
   (b) field 2 is a state — `open`, `closed` or `filtered`, compared
   **case-insensitively** and stored lowercase,
   (c) field 1 contains a `/` separating the port part from the protocol.
   Everything else is skipped and counted in `skipped`.
   Blank lines are not lines at all — they are counted nowhere. `lines` counts the
   **non-blank** input lines of `scan.txt`.
2. **Port field.** `22/tcp` → port `22`, protocol `tcp`. A range field `8000-8010/tcp`
   expands to one record per port from `8000` to `8010` **inclusive**, each carrying the
   same protocol, state and service.
3. **Service.** The service is field 3, when the line has one — the single token up to the
   next space, never the rest of the line (`80/tcp open Microsoft IIS httpd` → `Microsoft`).
   A line with exactly two fields has the empty service.
4. **Last probe wins.** When the same (port, protocol) appears more than once, the last
   line's state and service replace the earlier ones, and **every** earlier record for
   that (port, protocol) is counted in `superseded` — whether or not its state changed.
   Records produced by one range line are superseded individually.
5. **Verdict**, one per (port, protocol), baseline looked up **by port number** (the sheet
   has no protocol column). First matching rule wins:
   1. `unexpected` — the port is in the baseline with `expected` = `yes` and its state is
      **not** `open` (`closed` or `filtered`).
   2. `should-be-closed` — the port is in the baseline with `expected` = `no` and its
      state **is** `open`.
   3. `wrong-service` — the port is in the baseline with `expected` = `yes`, its state is
      `open`, and its service differs from the baseline service (**case-sensitive**; a
      missing service counts as different).
   4. `ok` — the port is in the baseline with `expected` = `yes`, its state is `open`, and
      its service matches the baseline service exactly.
   5. `ok` — the port is in the baseline with `expected` = `no` and its state is not
      `open`: it is closed the way the sheet wants it.
   6. `unbaselined` — the port is not in the baseline at all, whatever its state.
6. **Baseline rows** are trimmed on both sides. The header line and blank lines are
   ignored. A surviving row that does not have three fields with a numeric port is bad
   input: say which line, and exit non-zero.

## Output

Write exactly these files to `$OUT`.

**`out/ports.csv`** — header exactly `port,proto,state,service,verdict`, then one row per
**distinct** (port, protocol) scanned, sorted by `port` **ascending numerically**, ties by
`proto` **ascending (byte order)**. `service` is empty when the last line for that port
reported none, and no field is ever quoted or re-ordered. `state` is lowercase. `verdict`
is exactly one of `ok`, `wrong-service`, `unexpected`, `should-be-closed`, `unbaselined`.

**`out/summary.json`** — an object with exactly these keys:

| key | meaning |
|---|---|
| `lines` | non-blank lines in `scan.txt` |
| `ports` | distinct (port, protocol) pairs scanned (= rows in `ports.csv`) |
| `skipped` | lines rejected by rule 1 |
| `superseded` | records replaced by a later one for the same (port, protocol) |
| `open` | ports left with state `open` |
| `unbaselined` | ports whose verdict is `unbaselined` |
| `attention` | ports whose verdict is `wrong-service`, `unexpected` or `should-be-closed` |

## Messes to expect

- a line with no state at all (`3306/tcp`), and a stray log line that happens to have
  three fields
- `OPEN` in upper case, and one line padded with spaces on both sides
- the same port probed twice with the same state, and twice with **different** states
- `80` first reporting `Microsoft`, then `http` — the last line decides, so `80` is `ok`
- a range line whose ports are nowhere in the baseline
- a service field that is really two words, and a line with no service at all
- a baseline row for a port that was never scanned, and a baseline row padded with spaces

## Timebox

4 minutes. Python: two dicts (baseline by port, records by `(port, proto)`). Awk: one pass
per file, write `port<TAB>proto<TAB>row` and let `sort` order it.

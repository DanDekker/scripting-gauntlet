# 056-network-events

> "Firewall log for last night. What got through, what didn't, and who was loud?"

## Task

`in/events.log` is a firewall event log. Each line is a timestamp followed by
`KEY=VALUE` pairs:

```
2026-10-29T10:00:01Z SRC=10.0.0.5 DST=10.0.1.20 PROTO=TCP DPT=443 ACTION=ALLOW
```

## Rules

1. An event needs **`SRC`, `DPT` and `ACTION`**. A line missing any of them is
   **malformed**: skip it and count it. Do not guess a value.
2. `ACTION` is one of `ALLOW`, `DROP`, `REJECT`, but the log is not consistent about
   case — fold it to upper case before counting.
3. `blocked` means `DROP` or `REJECT`. `allowed` means `ALLOW`.
4. Report the **top 5** sources by attempt count.

## Output

**`out/actions.csv`** — header, then one row per action:

```
action,count
ALLOW,7
```

Ordered by `count` **descending**, ties by `action` ascending.

**`out/top_sources.csv`** — header, then at most 5 rows:

```
source,attempts
10.0.0.5,4
```

Ordered by `attempts` **descending**, ties by `source` ascending.

**`out/summary.json`** — exactly four keys: `events` (parsed events), `allowed`,
`blocked`, `skipped` (malformed lines).

## Messes to expect

- a line missing `DPT` — that is malformed, not a zero port
- an `ACTION=allow` in lower case
- a source that only appears on malformed lines, which therefore never appears in the
  ranking

## Timebox

4 minutes. Extract a key's value with a pattern, then count.

# 051-conn-states

> "Same netstat capture. How are the connections spread across states, and who are we
> talking to the most? I want a screenshot-ready answer."

## Task

`in/netstat-an.txt` is a captured BSD `netstat -an`, TCP only (same table as 050).

## Rules

1. A **data row** is a line whose first field starts with `tcp`; ignore the `udp4`/`udp6`
   rows, the heading and the column header.
2. The **state** is the last field of a data row. It is not normalized: print it as
   captured, `LISTEN` included.
3. The **remote address** is the 5th field with the port stripped at the **last** `.`.
   Rows whose 5th field is `*.*` have no peer — keep them out of the remote ranking.

## Output

**`out/states.csv`** — header exactly `state,count`, one row per state present, sorted by
`count` **descending**, ties by `state` **ascending (byte order)**.

**`out/remote_top.csv`** — header exactly `remote,connections`, at most **3** rows: the
remote addresses with the most connections, sorted `connections` **descending**, ties by
`remote` **ascending (byte order)**.

**`out/summary.json`** — exactly three keys: `tcp_rows` (tcp data rows), `connections`
(tcp data rows whose state is not `LISTEN`), `states` (distinct states seen).

## Messes to expect

- `LISTEN` rows with a `*.*` peer sitting in the same table
- several peers with a single connection each, so the tie-break decides third place
- `1.1.1.1` and `127.0.0.1` both at 1 — byte order puts `1.1.1.1` first
- `tcp46` as well as `tcp4`/`tcp6`

## Timebox

3 minutes. One `awk` building two accumulators, then two `sort`s.

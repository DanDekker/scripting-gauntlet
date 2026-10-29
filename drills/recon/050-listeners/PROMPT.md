# 050-listeners

> "Someone double-bound 8080 again and I can't trust lsof on that box. Here's a saved
> `netstat -an` — tell me everything that's listening, and what's shadowed."

## Task

`in/netstat-an.txt` is a captured BSD `netstat -an`, TCP only, no name resolution.

## Rules

1. The file has a heading line and a column header. A **data row** is a line whose first
   field starts with `tcp` — ignore the `udp4`/`udp6` rows and everything else.
2. A data row is a **listener** iff its **last** field is exactly `LISTEN`. Every other
   data row is a connection.
3. The **local address** is the 4th field, written `ADDRESS.PORT`. Split at the **last**
   `.`: `127.0.0.1.8080` → `127.0.0.1` + `8080`, `*.22` → `*` + `22`, `::1.5432` →
   `::1` + `5432`. Print the address exactly as captured (no rewriting of `*` or `::1`).
4. Two listener rows with the same (port, address) are **one** listener — dedupe.
5. A listener is **shadowed** when its address is not `*` and another listener on the same
   port has the wildcard address `*`. A wildcard/wildcard pair (IPv4 plus IPv6) shadows
   nothing.

## Output

**`out/listeners.csv`** — header exactly `port,address`, one row per distinct listener,
sorted by `port` **ascending numerically**, ties by `address` **ascending (byte order)**.

**`out/conflicts.csv`** — header exactly `port,address`, one row per shadowed listener,
same sort order. Header only when nothing is shadowed.

**`out/summary.json`** — exactly three keys: `tcp_rows` (tcp data rows, listeners and
connections), `listeners` (rows in `listeners.csv`), `conflicts` (rows in
`conflicts.csv`).

## Messes to expect

- `tcp46`, `tcp4` and `tcp6` rows in one table
- the same port on both an IPv4 and an IPv6 address (`5432`) — two listeners, no conflict
- the same port wildcard-bound *and* loopback-bound (`8080`) — that one is shadowed
- `*.631` listed twice, once per stack
- two `udp` rows that are not TCP and must not be counted

## Timebox

3 minutes. One `awk` to build `port,address` rows, one pass over that to find wildcards.

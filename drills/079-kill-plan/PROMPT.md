# 079-kill-plan

> "The box is thrashing and I have one shot. Give me a kill order that cannot take out
> init or my SSH daemon, and tell me what you refused to touch."

## Task

`in/ps.txt` is a `ps -eo pid,ppid,stat,%cpu,%mem,etime,comm` capture with a header.
`in/protected.txt` lists command names that must never be signalled (`#` comments and
blank lines included).

## Rules

1. Skip the header line (its first field is `PID`) and blank lines. Fields are
   whitespace-separated; `COMMAND` is the last field and contains no spaces.
2. **Hot** means `%CPU >= 20` or `%MEM >= 20` on its own.
3. A hot process is excluded from the plan when its pid is `1`, its `STAT` starts with
   `Z` (a zombie cannot be killed, only reaped), or its command is in the protected list.
   Count each excluded hot process in `skipped`.
4. Plan order: deepest process first (number of PPID hops until the chain reaches ppid 0
   or an unknown pid), then `%CPU` descending, then `pid` ascending.
5. Signal: `KILL` when `%MEM >= 40`, otherwise `TERM`. Do not invent a second phase.
6. A protected command with no hot processes changes nothing; it is not an error.

## Output

- `out/plan.csv` - header `pid,signal,command`, one row per planned kill, in plan order.
- `out/summary.json` - exactly four integers: `candidates` (rows written), `kill`, `term`,
  `skipped` (hot but excluded).

## Messes to expect

- a zombie burning CPU that must not be signalled
- a busy daemon that is protected
- a child whose parent is also hot
- `%CPU` just under the threshold, which must stay out of the plan

## Timebox

5 minutes. Parse the table once, compute depth from PPID, sort, print.

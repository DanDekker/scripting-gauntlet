# 075-load-triage

> "Four hosts paged me at once. Before I touch anything I need one line per host: what is
> saturated, and the numbers that prove it."

## Task

`in/hosts/<host>/` holds a small capture per host:

- `loadavg` - one line in `/proc/loadavg` form: `load1 load5 load15 running/total lastpid`.
- `nproc` - the number of CPUs.
- `vmstat` - a `vmstat 1 3` capture: two header lines, then three samples.

`vmstat` columns are the classic 17: `r b swpd free buff cache si so bi bo in cs us sy id wa st`.

## Rules

1. Treat a data row as `NF >= 17` with an integer first field; skip everything else.
2. Average each host's samples for `r`, `wa` and `us + sy`.
3. Classify with exactly this precedence:
   1. `memory` - **any** sample has `si + so > 0`;
   2. `io` - average `wa >= 10`;
   3. `cpu` - average `r >= 2 * nproc` **and** average `us + sy >= 80`;
   4. `healthy` - everything else.
4. `load1_per_cpu` is `load1 / nproc`, printed with two decimals. `r_avg`, `wa_avg` and
   `busy_pct` print with one decimal.
5. A host with no samples, a non-positive `nproc`, or a missing file is an error: name the
   host on stderr and exit non-zero.

## Output

- `out/triage.csv` - header `host,verdict,load1_per_cpu,r_avg,wa_avg,busy_pct`, one row per
  host, sorted by `host` ascending in byte order.
- `out/summary.json` - exactly two integers: `hosts` and `saturated` (verdict is not
  `healthy`).

## Messes to expect

- a host whose load is high only because of swap, not CPU
- a host whose run queue is long while CPUs are idle-ish
- an idle host that must still be reported
- two header lines to skip, not one

## Timebox

4 minutes. One awk pass per host, verdict from the averages, print one line.

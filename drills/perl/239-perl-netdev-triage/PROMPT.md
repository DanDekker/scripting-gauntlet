# 239-perl-netdev-triage

> "A packet-loss spike is impacting our production cluster. We have a snapshot of
> `/proc/net/dev` across host interfaces. We need an automated triage script to parse
> the kernel interface metrics, sum traffic and error counts, classify interface health,
> and identify degrading interfaces."

## Input

`in/net_dev.txt` — snapshot of `/proc/net/dev`:
- The first 2 lines are header lines (`Inter-| Receive ... | Transmit` and column names).
- Subsequent lines represent network interfaces with 16 numeric columns following the interface name:
  `   <interface>: <rx_bytes> <rx_packets> <rx_errs> <rx_drop> <rx_fifo> <rx_frame> <rx_compressed> <rx_multicast> <tx_bytes> <tx_packets> <tx_errs> <tx_drop> <tx_fifo> <tx_colls> <tx_carrier> <tx_compressed>`

Example:
```text
Inter-|   Receive                                                |  Transmit
 face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
    lo: 10485760   20000    0    0    0     0          0         0 10485760   20000    0    0    0     0       0          0
  eth0: 52428800   80000  120   15    0     0          0         0 26214400   40000   10    2    0     0       0          0
  eth1:        0       0    0    0    0     0          0         0        0       0    0    0    0     0       0          0
 wlan0: 15728640   25000    0    0    0     0          0         0  5242880   10000    0    0    0     0       0          0
docker0: 2097152    3000    5    0    0     0          0         0  1048576    1500    0    0    0     0       0          0
```

## Rules

1. Parse interface lines:
   - Interface name is everything before the colon (`:`), stripped of leading and trailing whitespace.
   - Column values after the colon:
     - Receive: col 0=`rx_bytes`, col 1=`rx_packets`, col 2=`rx_errs`, col 3=`rx_drop`.
     - Transmit: col 8=`tx_bytes`, col 9=`tx_packets`, col 10=`tx_errs`, col 11=`tx_drop`.
2. Compute metrics:
   - `total_bytes = rx_bytes + tx_bytes`
   - `total_packets = rx_packets + tx_packets`
   - `total_errors = rx_errs + tx_errs`
   - `total_drops = rx_drop + tx_drop`
3. Classify `status`:
   - If `total_bytes == 0`: `"DOWN"`
   - Else if `total_errors > 0 || total_drops > 0`: `"DEGRADED"`
   - Else: `"HEALTHY"`
4. **`out/interfaces.tsv`** — tab-separated values (`\t`):
   - Header: `interface\tstatus\ttotal_bytes\ttotal_packets\ttotal_errors\ttotal_drops`
   - Sorted by `total_bytes` **descending** numerically (`<=>`); ties broken by `interface` **ascending** in ASCII order (`cmp`).
5. **`out/summary.json`** — compact JSON object with keys:
   - `total_interfaces`: count of parsed interfaces.
   - `healthy_count`: count of interfaces with status `HEALTHY`.
   - `degraded_count`: count of interfaces with status `DEGRADED`.
   - `down_count`: count of interfaces with status `DOWN`.
   - `total_traffic_bytes`: sum of `total_bytes` across all interfaces.
   - `top_interface`: `interface` name with the highest `total_bytes` (tie broken by `interface` ascending).

## Messes to expect

- Two leading header lines that do not contain a colon.
- Variable whitespace before and after the interface name and between numbers.
- In Perl, `split(/\s+/, $line)` on a line with leading whitespace includes an empty string at index 0, shifting column indices. Split on colon first, or use `split(' ', $str)` (awk mode).

## Timebox

Five minutes.


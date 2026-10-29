#!/usr/bin/env bash
# 079-kill-plan - one awk pass, depth from PPID, sort deepest and hottest first.
set -euo pipefail
export LC_ALL=C

inp="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
[[ -r "$inp/ps.txt" && -r "$inp/protected.txt" ]] \
  || { echo "missing ps.txt or protected.txt" >&2; exit 1; }
mkdir -p "$outdir"

plan=$(mktemp)
trap 'rm -f "$plan"' EXIT

awk -v protected="$inp/protected.txt" -v plan="$plan" -v summary="$outdir/summary.json" '
  FNR == NR {
    line = $0; sub(/[ \t\r]+$/, "", line)
    if (line != "" && substr(line, 1, 1) != "#") prot[line] = 1
    next
  }
  NF < 7 || $1 == "PID" { next }
  {
    pid = $1 + 0
    ppid[pid] = $2 + 0; stat[pid] = $3; cpu[pid] = $4 + 0; mem[pid] = $5 + 0; cmd[pid] = $7
    alive[pid] = 1
  }
  function hops(start,   h, p, guard) {
    h = 0; p = start; guard = 0
    while ((p in ppid) && ppid[p] != 0 && (ppid[p] in alive) && guard < 64) {
      p = ppid[p]; h++; guard++
    }
    return h
  }
  END {
    candidates = 0; killed = 0; termed = 0; skipped = 0
    for (pid in alive) {
      if (cpu[pid] < 20 && mem[pid] < 20) continue
      if (pid == 1 || substr(stat[pid], 1, 1) == "Z" || (cmd[pid] in prot)) { skipped++; continue }
      sig = (mem[pid] >= 40) ? "KILL" : "TERM"
      if (sig == "KILL") killed++; else termed++
      candidates++
      printf "%d,%.1f,%d,%s,%s\n", hops(pid), cpu[pid], pid, sig, cmd[pid] > plan
    }
    close(plan)
    printf "{\"candidates\":%d,\"kill\":%d,\"term\":%d,\"skipped\":%d}\n", \
      candidates, killed, termed, skipped > summary
    close(summary)
  }' "$inp/protected.txt" "$inp/ps.txt"

{
  printf 'pid,signal,command\n'
  LC_ALL=C sort -t, -k1,1nr -k2,2nr -k3,3n "$plan" | awk -F, '{ printf "%s,%s,%s\n", $3, $4, $5 }'
} > "$outdir/plan.csv"

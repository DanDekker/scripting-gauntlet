#!/usr/bin/env bash
# 051-conn-states — one pass, two accumulators, two sorts.
set -euo pipefail

src="${IN:?IN not set}/netstat-an.txt"
outdir="${OUT:?OUT not set}"
[ -r "$src" ] || { echo "cannot read $src" >&2; exit 1; }
mkdir -p "$outdir"

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

awk -v states="$tmp/states.body" -v remotes="$tmp/remote.body" -v counts="$tmp/counts" '
{
  if ($1 !~ /^tcp/) next
  tcp++
  state = $NF
  if (!(state in seen)) { seen[state] = 1; nstates++ }
  sc[state]++
  if (state != "LISTEN") connections++
  if ($5 == "*.*") next
  remote = $5
  sub(/\.[^.]*$/, "", remote)
  rc[remote]++
}
END {
  for (s in sc) printf "%s,%d\n", s, sc[s] > states
  for (r in rc) printf "%s,%d\n", r, rc[r] > remotes
  printf "%d %d %d\n", tcp, connections, nstates > counts
  close(states)
  close(remotes)
  close(counts)
}
' "$src"

{
  printf 'state,count\n'
  LC_ALL=C sort -t, -k2,2nr -k1,1 "$tmp/states.body"
} > "$outdir/states.csv"

{
  printf 'remote,connections\n'
  LC_ALL=C sort -t, -k2,2nr -k1,1 "$tmp/remote.body" | sed -n '1,3p'
} > "$outdir/remote_top.csv"

read -r tcp_rows connections nstates < "$tmp/counts"
printf '{"tcp_rows":%d,"connections":%d,"states":%d}\n' \
  "$tcp_rows" "$connections" "$nstates" > "$outdir/summary.json"

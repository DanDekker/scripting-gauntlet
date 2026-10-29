#!/usr/bin/env bash
# 050-listeners — state is the last field, port is after the last dot.
set -euo pipefail

src="${IN:?IN not set}/netstat-an.txt"
outdir="${OUT:?OUT not set}"
[ -r "$src" ] || { echo "cannot read $src" >&2; exit 1; }
mkdir -p "$outdir"

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

awk -v rows="$tmp/listeners.body" -v count="$tmp/tcp_rows" '
{
  if ($1 !~ /^tcp/) next
  tcp++
  if ($NF != "LISTEN") next
  loc = $4
  port = loc
  sub(/^.*\./, "", port)
  addr = substr(loc, 1, length(loc) - length(port) - 1)
  key = port SUBSEP addr
  if (key in seen) next
  seen[key] = 1
  printf "%d,%s\n", port + 0, addr > rows
}
END {
  printf "%d\n", tcp > count
  close(rows)
  close(count)
}
' "$src"

# passes over listeners.body: wildcard present on this port?
awk -F, -v body="$tmp/conflict.body" '
{ n++; port[n] = $1 + 0; addr[n] = $2; if ($2 == "*") wild[$1 + 0] = 1 }
END {
  for (i = 1; i <= n; i++) {
    if (addr[i] != "*" && (port[i] in wild)) printf "%d,%s\n", port[i], addr[i] > body
  }
  close(body)
}' "$tmp/listeners.body"

{
  printf 'port,address\n'
  LC_ALL=C sort -t, -k1,1n -k2,2 "$tmp/listeners.body"
} > "$outdir/listeners.csv"

{
  printf 'port,address\n'
  if [ -s "$tmp/conflict.body" ]; then
    LC_ALL=C sort -t, -k1,1n -k2,2 "$tmp/conflict.body"
  fi
} > "$outdir/conflicts.csv"

tcp_rows=$(cat "$tmp/tcp_rows")
listeners=$(awk 'END { print NR + 0 }' "$tmp/listeners.body")
if [ -s "$tmp/conflict.body" ]; then
  conflicts=$(awk 'END { print NR + 0 }' "$tmp/conflict.body")
else
  conflicts=0
fi
printf '{"tcp_rows":%d,"listeners":%d,"conflicts":%d}\n' \
  "$tcp_rows" "$listeners" "$conflicts" > "$outdir/summary.json"

#!/usr/bin/env bash
# 048-ps-snapshot — normalize the table once, then sort it twice.
set -euo pipefail

src="${IN:?IN not set}/ps-snapshot.txt"
outdir="${OUT:?OUT not set}"
[ -r "$src" ] || { echo "cannot read $src" >&2; exit 1; }
mkdir -p "$outdir"

body=$(mktemp)
trap 'rm -f "$body"' EXIT
sorted=$(mktemp)
trap 'rm -f "$body" "$sorted"' EXIT

# pid,ppid,rss_kb,cpu,command — the command is fields 5..NF rejoined.
awk '
NR == 1 { next }
NF < 5  { next }
{
  cmd = $5
  for (i = 6; i <= NF; i++) cmd = cmd " " $i
  printf "%d,%d,%d,%.1f,%s\n", $1 + 0, $2 + 0, $3 + 0, $4 + 0, cmd
}' "$src" > "$body"

LC_ALL=C sort -t, -k3,3nr -k1,1n "$body" > "$sorted"
{
  printf 'pid,ppid,rss_kb,cpu,command\n'
  head -n 5 "$sorted"
} > "$outdir/top_rss.csv"

{
  printf 'command,processes\n'
  awk -F, '
  { split($5, token, " "); name = token[1]; if (substr(name, 1, 1) != "[") sub(/^.*\//, "", name); c[name]++ }
  END { for (n in c) printf "%s,%d\n", n, c[n] }' "$body" \
    | LC_ALL=C sort -t, -k2,2nr -k1,1
} > "$outdir/commands.csv"

awk -F, -v outdir="$outdir" '
{
  total += $3
  split($5, token, " ")
  name = token[1]
  if (substr(name, 1, 1) != "[") sub(/^.*\//, "", name)
  if (!(name in seen)) { seen[name] = 1; distinct++ }
}
END {
  f = outdir "/summary.json"
  printf "{\"processes\":%d,\"total_rss_kb\":%d,\"commands\":%d}\n", NR, total, distinct > f
  close(f)
}' "$body"

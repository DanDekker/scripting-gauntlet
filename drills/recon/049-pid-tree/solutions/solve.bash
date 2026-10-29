#!/usr/bin/env bash
# 049-pid-tree — memoized depth in awk, queue walk for the descendants.
set -euo pipefail

src="${IN:?IN not set}/ps-snapshot.txt"
outdir="${OUT:?OUT not set}"
[ -r "$src" ] || { echo "cannot read $src" >&2; exit 1; }
mkdir -p "$outdir"

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

awk -v tree="$tmp/tree.body" -v orph="$tmp/orphans.body" -v desc="$tmp/descendants.raw" '
NR == 1 { next }
NF < 5  { next }
{
  pid = $1 + 0
  pp = $2 + 0
  PP[pid] = pp
  cmd = $5
  for (i = 6; i <= NF; i++) cmd = cmd " " $i
  CMD[pid] = cmd
  HAVE[pid] = 1
  ORDER[++n] = pid
  kids[pp] = (kids[pp] == "" ? "" : kids[pp] " ") pid
}
END {
  for (i = 1; i <= n; i++) {
    p = ORDER[i]
    printf "%d,%d,%d,%s\n", p, PP[p], depth(p), CMD[p] > tree
  }
  close(tree)

  for (i = 1; i <= n; i++) {
    p = ORDER[i]
    if (PP[p] != 0 && !(PP[p] in HAVE)) printf "%d,%d,%s\n", p, PP[p], CMD[p] > orph
  }
  close(orph)

  q = 0
  m = split(kids[205], seed, " ")
  for (i = 1; i <= m; i++) queue[++q] = seed[i] + 0
  for (h = 1; h <= q; h++) {
    p = queue[h]
    print p > desc
    m = split(kids[p], nxt, " ")
    for (j = 1; j <= m; j++) queue[++q] = nxt[j] + 0
  }
  close(desc)
}
function depth(p,   parent) {
  if (p in D) return D[p]
  parent = PP[p]
  if (!(parent in HAVE)) { D[p] = 0; return 0 }
  D[p] = depth(parent) + 1
  return D[p]
}
' "$src"

{
  printf 'pid,ppid,depth,command\n'
  LC_ALL=C sort -t, -k3,3n -k1,1n "$tmp/tree.body"
} > "$outdir/tree.csv"

LC_ALL=C sort -n "$tmp/descendants.raw" > "$outdir/descendants.txt"

{
  printf 'pid,ppid,command\n'
  if [ -f "$tmp/orphans.body" ]; then
    LC_ALL=C sort -t, -k1,1n "$tmp/orphans.body"
  fi
} > "$outdir/orphans.csv"

awk -F, -v outdir="$outdir" '
{ rows++; if ($3 + 0 == 0) roots++; if ($3 + 0 > deep) deep = $3 + 0 }
END {
  f = outdir "/summary.json"
  printf "{\"processes\":%d,\"roots\":%d,\"max_depth\":%d}\n", rows, roots, deep > f
  close(f)
}' "$tmp/tree.body"

#!/usr/bin/env bash
# 129-crawl-frontier - awk does the whole job: parse the graph, then BFS with two
# parallel queue arrays. bash 3.2 has no associative arrays, awk does.
set -euo pipefail
export LC_ALL=C

inp="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
[[ -r "$inp/sitemap.txt" && -r "$inp/config.json" ]] \
  || { echo "missing sitemap.txt or config.json" >&2; exit 1; }
mkdir -p "$outdir"

seed=$(jq -r '.seed' "$inp/config.json")
maxdepth=$(jq -r '.max_depth' "$inp/config.json")
samehost=$(jq -r '.same_host // ""' "$inp/config.json")
limit=$(jq -r '.limit' "$inp/config.json")

awk -v seed="$seed" -v maxdepth="$maxdepth" -v samehost="$samehost" -v limit="$limit" \
    -v rowfile="$outdir/pages.csv" -v sumfile="$outdir/summary.json" '
function trim(s) { sub(/^[ \t\r]+/, "", s); sub(/[ \t\r]+$/, "", s); return s }
function normalise(u,   i) {
  u = trim(u)
  i = index(u, "#")
  if (i > 0) u = substr(u, 1, i - 1)
  return u
}
function absolute(u) { return u ~ /^https?:\/\/[^ \t]+$/ }
function host_of(u,   r, i) {
  r = u
  sub(/^[A-Za-z][A-Za-z0-9+.-]*:\/\//, "", r)
  i = index(r, "/")
  if (i > 0) r = substr(r, 1, i - 1)
  return r
}
function href_of(line,   i, s, j) {
  i = index(line, "href=\"")
  if (i == 0) return ""
  s = substr(line, i + 6)
  j = index(s, "\"")
  if (j == 0) return ""
  return substr(s, 1, j - 1)
}
# --- 1. the saved link graph -------------------------------------------------
{
  line = $0
  sub(/\r$/, "", line)
  t = trim(line)
  if (t == "") next
  if (substr(t, 1, 1) == "<") {
    if (owner_i > 0) {
      u = normalise(href_of(t))
      if (absolute(u) && u != owner) { nlinks[owner_i]++; link[owner_i, nlinks[owner_i]] = u }
    }
    next
  }
  if (absolute(t)) {
    u = normalise(t)
    if (!(u in pidx)) { npages++; page[npages] = u; pidx[u] = npages }
    owner = u
    owner_i = pidx[u]
  }
}
END {
  # --- 2. inbound over the whole site graph (distinct sources) ----------------
  for (p = 1; p <= npages; p++) {
    src = page[p]
    for (k = 1; k <= nlinks[p]; k++) {
      tgt = link[p, k]
      if (!(tgt in pidx)) continue
      pair = tgt SUBSEP src
      if (pair in counted) continue
      counted[pair] = 1
      inb[tgt]++
    }
  }
  # --- 3. breadth-first from the seed ---------------------------------------
  nvis = 0; skipped = 0; limit_reached = "false"
  seed = normalise(seed)
  if (seed in pidx) {
    head = 1; tail = 1
    qurl[1] = seed; qdep[1] = 0
    discovered[seed] = 1
    while (head <= tail && nvis < limit) {
      u = qurl[head]; d = qdep[head]; head++
      nvis++; ord[nvis] = u; visit[u] = d
      if (d >= maxdepth) continue
      p = pidx[u]
      for (k = 1; k <= nlinks[p]; k++) {
        v = link[p, k]
        if (!(v in pidx) || (v in discovered) || (v in visit)) { skipped++; continue }
        if (samehost != "" && host_of(v) != samehost) { skipped++; continue }
        discovered[v] = 1
        tail++; qurl[tail] = v; qdep[tail] = d + 1
      }
    }
    if (nvis == limit && head <= tail) limit_reached = "true"
  }
  # --- 4. outputs -----------------------------------------------------------
  print "url,depth,inbound" > rowfile
  maxd = 0
  for (i = 1; i <= nvis; i++) {
    u = ord[i]
    if (visit[u] > maxd) maxd = visit[u]
    row = sprintf("%s,%d,%d", u, visit[u], (u in inb) ? inb[u] : 0)
    print row > rowfile
  }
  summary = sprintf("{\"visited\":%d,\"skipped\":%d,\"limit_reached\":%s,\"max_depth_reached\":%d,\"orphan\":%d}", nvis, skipped, limit_reached, maxd, npages - nvis)
  print summary > sumfile
}
' "$inp/sitemap.txt"

echo "129-crawl-frontier: wrote $outdir/pages.csv and $outdir/summary.json"

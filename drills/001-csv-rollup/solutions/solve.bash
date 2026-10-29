#!/usr/bin/env bash
# 001-csv-rollup — awk, because this is a five-minute job.
set -euo pipefail

src="${IN:?IN not set}/orders.csv"
outdir="${OUT:?OUT not set}"
[ -r "$src" ] || { echo "cannot read $src" >&2; exit 1; }
mkdir -p "$outdir"

awk -F',' -v outdir="$outdir" '
function trim(s) { gsub(/\r/, "", s); gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
{
  if (tolower(trim($1)) == "order_id") next   # header
  if (trim($0) == "") next                   # blank line
  id = trim($1)
  if (id == "") next
  ts = trim($6)
  if (!(id in seen_id) || ts > latest[id]) {  # later updated_at wins
    seen_id[id] = 1
    latest[id] = ts
    region[id] = trim($3)
    status[id] = tolower(trim($4))
    amount[id] = trim($5)
  }
}
END {
  for (id in seen_id) {
    if (status[id] != "paid") continue
    a = amount[id]
    gsub(/[$]/, "", a); gsub(/,/, "", a)
    if (a == "" || a !~ /^-?[0-9]+(\.[0-9]+)?$/) { dropped++; continue }
    r = region[id]
    if (r != "") r = toupper(substr(r, 1, 1)) tolower(substr(r, 2))
    if (!(r in have)) { have[r] = 1; names[++n] = r }
    count[r]++
    sum[r] += a + 0
    orders++
    revenue += a + 0
  }

  # insertion sort: revenue desc, then region asc
  for (i = 2; i <= n; i++) {
    v = names[i]; j = i - 1
    while (j >= 1 && (sum[names[j]] < sum[v] || (sum[names[j]] == sum[v] && names[j] > v))) {
      names[j + 1] = names[j]; j--
    }
    names[j + 1] = v
  }

  f = outdir "/regions.csv"
  printf "region,orders,revenue\n" > f
  for (i = 1; i <= n; i++)
    printf "%s,%d,%.2f\n", names[i], count[names[i]], sum[names[i]] > f
  close(f)

  g = outdir "/summary.json"
  printf "{\"orders\":%d,\"regions\":%d,\"revenue\":%.2f,\"dropped\":%d}\n", orders, n, revenue, dropped > g
  close(g)
}
' "$src"

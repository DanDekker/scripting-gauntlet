#!/usr/bin/env bash
# 130-rate-limit-headers - one streaming awk pass. A block is flushed the moment the
# next request line shows up, so no buffering is needed.
set -euo pipefail
export LC_ALL=C

inp="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
[[ -r "$inp/responses.log" && -r "$inp/now.txt" ]] \
  || { echo "missing responses.log or now.txt" >&2; exit 1; }
mkdir -p "$outdir"

now=$(tr -d '[:space:]' < "$inp/now.txt")
[[ "$now" =~ ^[0-9]+$ ]] || { echo "$inp/now.txt: not an epoch integer: $now" >&2; exit 1; }

awk -v now="$now" -v rowfile="$outdir/responses.csv" -v sumfile="$outdir/summary.json" '
function trim(s) { sub(/^[ \t\r]+/, "", s); sub(/[ \t\r]+$/, "", s); return s }
function month_num(m,   i, names) {
  split("jan feb mar apr may jun jul aug sep oct nov dec", names, " ")
  for (i = 1; i <= 12; i++) if (names[i] == m) return i
  return -1
}
# Howard Hinnant days-from-civil: no date library needed, and no local time zone.
function days_from_civil(y, m, d,   era, yoe, doy, doe) {
  if (m <= 2) y -= 1
  era = (y >= 0) ? int(y / 400) : int((y - 399) / 400)
  yoe = y - era * 400
  doy = int((153 * (m + (m > 2 ? -3 : 9)) + 2) / 5) + d - 1
  doe = yoe * 365 + int(yoe / 4) - int(yoe / 100) + doy
  return era * 146097 + doe - 719468
}
# "Thu, 01 Jan 2026 00:01:00 GMT" -> epoch seconds, or -1 when it does not parse.
function http_date_epoch(s,   f, n, day, mon, year, clock, t, mi) {
  gsub(/,/, " ", s)
  s = trim(s)
  n = split(s, f, /[ \t]+/)
  if (n < 5) return -1
  day = f[2] + 0
  mi = month_num(tolower(f[3])); if (mi < 0) return -1
  year = f[4] + 0
  if (split(f[5], t, ":") != 3) return -1
  return days_from_civil(year, mi, day) * 86400 + (t[1] + 0) * 3600 + (t[2] + 0) * 60 + (t[3] + 0)
}
function clear_headers(   k) { for (k in hdr) delete hdr[k] }
function flush(   rem_known, rem, wait_known, wait, action, ra, rs, ep, row, v) {
  if (!inblock) return
  inblock = 0
  if (!have_status) { skipped++; return }

  rem_known = 0; rem = 0
  v = hdr["x-ratelimit-remaining"]
  if (v ~ /^[0-9]+$/) { rem_known = 1; rem = v + 0 }

  wait_known = 0; wait = 0
  if (status == 429) {
    ra = hdr["retry-after"]
    if (ra ~ /^[0-9]+$/) { wait_known = 1; wait = ra + 0 }
    else if (ra != "") {
      ep = http_date_epoch(ra)
      if (ep != -1) { wait_known = 1; wait = ep - now; if (wait < 0) wait = 0 }
    }
    if (!wait_known) {
      rs = hdr["x-ratelimit-reset"]
      if (rs ~ /^[0-9]+$/) { wait_known = 1; wait = rs - now; if (wait < 0) wait = 0 }
    }
  }

  if (status == 429) { blocked++; action = wait_known ? "wait" : "wait-unknown" }
  else if (rem_known && rem == 0) { exhausted++; action = "hold" }
  else action = "proceed"
  if (wait_known) total_wait += wait

  row = sprintf("%d,%s,%s,%s", status, rem_known ? rem : "", wait_known ? wait : "", action)
  print row > rowfile
  responses++
}
BEGIN {
  inblock = 0; have_status = 0; status = 0
  responses = 0; skipped = 0; blocked = 0; exhausted = 0; total_wait = 0
  print "status,remaining,wait,action" > rowfile
}
{
  line = $0
  sub(/\r$/, "", line)
  t = trim(line)
  if (t == "") next
  if (t ~ /^[A-Z]+[ \t]+[^ \t]+[ \t]+HTTP\/[0-9]+(\.[0-9]+)?$/) {
    flush()
    inblock = 1; have_status = 0; clear_headers()
    next
  }
  if (!inblock) next
  if (!have_status) {
    if (substr(t, 1, 5) == "HTTP/" && match(t, /HTTP\/[0-9.]+[ \t]+[0-9][0-9][0-9]/)) {
      v = substr(t, RSTART, RLENGTH)
      sub(/^HTTP\/[0-9.]+[ \t]+/, "", v)
      status = v + 0
      have_status = 1
    }
    next
  }
  i = index(t, ":")
  if (i == 0) next
  hdr[tolower(trim(substr(t, 1, i - 1)))] = trim(substr(t, i + 1))
}
END {
  flush()
  summary = sprintf("{\"responses\":%d,\"skipped\":%d,\"blocked\":%d,\"exhausted\":%d,\"total_wait\":%d}", responses, skipped, blocked, exhausted, total_wait)
  print summary > sumfile
}
' "$inp/responses.log"

echo "130-rate-limit-headers: wrote $outdir/responses.csv and $outdir/summary.json"

#!/usr/bin/env bash
# 072-cron-expand - awk holds the tables; the shell only opens the file.
set -euo pipefail

src="${IN:?IN not set}/jobs.txt"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"
[[ -f "$src" ]] || { echo "missing $src" >&2; exit 1; }

awk -v outdir="$outdir" '
function trim(s) { gsub(/^[ \t\r]+|[ \t\r]+$/, "", s); return s }
function fail(msg) { print msg > "/dev/stderr"; failed = 1; exit 1 }
function nameval(tok, kind,   u) {
  u = toupper(tok)
  if (kind == "month" && (u in MON)) return MON[u]
  if (kind == "dow" && (u in DOW)) return DOW[u]
  if (tok ~ /^[0-9]+$/) return tok + 0
  return ""
}
function values(spec, lo, hi, kind,   parts, n, i, part, step, a, b, v, mark, s, slash, dash) {
  for (v = lo; v <= hi; v++) mark[v] = 0
  n = split(spec, parts, ",")
  for (i = 1; i <= n; i++) {
    part = parts[i]
    step = 1
    slash = index(part, "/")
    if (slash) { step = substr(part, slash + 1); part = substr(part, 1, slash - 1) }
    if (step !~ /^[0-9]+$/ || step + 0 < 1) return ""
    if (part == "*") { a = lo; b = hi }
    else if (index(part, "-")) {
      dash = index(part, "-")
      a = substr(part, 1, dash - 1); b = substr(part, dash + 1)
    } else { a = part; b = part }
    a = nameval(a, kind); b = nameval(b, kind)
    if (a == "" || b == "") return ""
    if (a + 0 > b + 0) return ""
    for (v = a + 0; v <= b + 0; v += step + 0) mark[v] = 1
  }
  if (kind == "dow" && mark[7]) mark[0] = 1
  s = ""
  for (v = lo; v <= (kind == "dow" ? 6 : hi); v++)
    if (mark[v]) s = s (s == "" ? "" : ",") v
  return s
}
function count(s,   tmp) { return split(s, tmp, ",") }
BEGIN {
  split("JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC", M, " ")
  for (i = 1; i <= 12; i++) MON[M[i]] = i
  split("SUN MON TUE WED THU FRI SAT", D, " ")
  for (i = 1; i <= 7; i++) DOW[D[i]] = i - 1
  printf "{" > (outdir "/schedule.json")
  first = 1
}
{
  line = trim($0)
  if (line == "" || substr(line, 1, 1) == "#") next
  n = split(line, F, /[ \t]+/)
  if (n != 6) fail("line " FNR ": expected job plus 5 fields: " line)
  job = F[1]
  if (job !~ /^[a-z0-9_-]+$/) fail("line " FNR ": bad job name " job)
  m = values(F[2], 0, 59, "minute")
  h = values(F[3], 0, 23, "hour")
  dom = values(F[4], 1, 31, "dom")
  mon = values(F[5], 1, 12, "month")
  dow = values(F[6], 0, 7, "dow")
  if (m == "") fail(job ": bad minute field: " F[2])
  if (h == "") fail(job ": bad hour field: " F[3])
  if (dom == "") fail(job ": bad dom field: " F[4])
  if (mon == "") fail(job ": bad month field: " F[5])
  if (dow == "") fail(job ": bad dow field: " F[6])
  printf "%s\"%s\":{\"minute\":[%s],\"hour\":[%s],\"dom\":[%s],\"month\":[%s],\"dow\":[%s]}", \
    (first ? "" : ","), job, m, h, dom, mon, dow > (outdir "/schedule.json")
  first = 0
  jobs++
  slots += count(m) * count(h)
}
END {
  if (failed) exit 1
  printf "}\n" > (outdir "/schedule.json")
  close(outdir "/schedule.json")
  printf "{\"jobs\":%d,\"slots\":%d}\n", jobs, slots > (outdir "/summary.json")
  close(outdir "/summary.json")
}' "$src"

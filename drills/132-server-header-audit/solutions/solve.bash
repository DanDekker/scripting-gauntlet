#!/usr/bin/env bash
# 132-server-header-audit - one streaming awk pass: a block is flushed when the next
# request line shows up, then five checks are applied in canonical order.
set -euo pipefail
export LC_ALL=C

inp="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
[[ -r "$inp/responses.txt" ]] || { echo "missing $inp/responses.txt" >&2; exit 1; }
mkdir -p "$outdir"

awk -v findfile="$outdir/findings.csv" -v sumfile="$outdir/summary.json" '
function trim(s) { sub(/^[ \t\r]+/, "", s); sub(/[ \t\r]+$/, "", s); return s }
function clear_headers(   k) { for (k in hdr) delete hdr[k] }
# Why check i fails: "" when it passes, else missing / weak / wrong-value.
function why(i,   v, lv, rest, cut_at) {
  if (!(HK[i] in hdr)) return "missing"
  v = hdr[HK[i]]
  if (i == 1) {
    lv = tolower(v)
    if (!match(lv, /max-age=/)) return "weak"
    rest = substr(lv, RSTART + 8)
    cut_at = index(rest, ";")
    if (cut_at > 0) rest = substr(rest, 1, cut_at - 1)
    rest = trim(rest)
    if (rest ~ /^[0-9]+$/ && rest + 0 > 0) return ""
    return "weak"
  }
  if (i == 2) {
    if (index(v, "*") > 0) return "weak"
    return ""
  }
  lv = tolower(trim(v))
  if (i == 3) return (lv == "nosniff") ? "" : "wrong-value"
  if (i == 4) return (lv == "deny" || lv == "sameorigin") ? "" : "wrong-value"
  if (lv == "no-referrer" || lv == "same-origin" || lv == "strict-origin" || lv == "strict-origin-when-cross-origin") return ""
  return "wrong-value"
}
function flush(   i, r, bad) {
  if (!inblock) return
  inblock = 0
  if (!have_status) { skipped++; return }
  responses++
  if (status >= 300 && status <= 399) { redirect++; return }
  if (status >= 400 && status <= 599) { error++; return }
  checked++
  bad = 0
  for (i = 1; i <= 5; i++) {
    r = why(i)
    if (r != "") {
      printf "%s,%d,%s,%s\n", url, status, HN[i], r > findfile
      findings++
      bad = 1
    }
  }
  if (bad) failed++; else passed++
}
BEGIN {
  HN[1] = "Strict-Transport-Security"; HK[1] = "strict-transport-security"
  HN[2] = "Content-Security-Policy";   HK[2] = "content-security-policy"
  HN[3] = "X-Content-Type-Options";    HK[3] = "x-content-type-options"
  HN[4] = "X-Frame-Options";           HK[4] = "x-frame-options"
  HN[5] = "Referrer-Policy";           HK[5] = "referrer-policy"
  responses = 0; skipped = 0; checked = 0; passed = 0; failed = 0
  redirect = 0; error = 0; findings = 0
  inblock = 0; status_seen = 0; have_status = 0; status = 0; url = ""
  printf "url,status,header,reason\n" > findfile
}
{
  line = $0
  sub(/\r$/, "", line)
  t = trim(line)
  if (t == "") next
  if (t ~ /^[A-Z]+[ \t]+[^ \t]+[ \t]+HTTP\/[0-9]+(\.[0-9]+)?$/) {
    flush()
    inblock = 1; status_seen = 0; have_status = 0; status = 0
    split(t, parts, /[ \t]+/)
    url = parts[2]
    clear_headers()
    next
  }
  if (!inblock) next
  if (!status_seen) {
    if (substr(t, 1, 5) != "HTTP/") next
    status_seen = 1
    if (match(t, /HTTP\/[0-9.]+[ \t]+[0-9][0-9][0-9]/)) {
      code = substr(t, RSTART, RLENGTH)
      sub(/^HTTP\/[0-9.]+[ \t]+/, "", code)
      status = code + 0
      have_status = 1
    }
    next
  }
  if (!have_status) next
  colon = index(t, ":")
  if (colon == 0) next
  name = trim(substr(t, 1, colon - 1))
  if (name !~ /^[A-Za-z0-9-]+$/) next
  hdr[tolower(name)] = trim(substr(t, colon + 1))
}
END {
  flush()
  summary = sprintf("{\"responses\":%d,\"skipped\":%d,\"checked\":%d,\"pass\":%d,\"fail\":%d,\"redirect\":%d,\"error\":%d,\"findings\":%d}", responses, skipped, checked, passed, failed, redirect, error, findings)
  print summary > sumfile
  close(findfile)
  close(sumfile)
}' "$inp/responses.txt"

echo "132-server-header-audit: wrote $outdir/findings.csv and $outdir/summary.json"

#!/usr/bin/env bash
# 125-pii-scan - awk finds candidates per kind, then resolves overlaps left to right.
set -euo pipefail
export LC_ALL=C

src="${IN:?IN not set}/tickets.txt"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"
[[ -f "$src" ]] || { echo "missing $src" >&2; exit 1; }

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

awk -v rows="$scratch/rows.csv" -v kinds="$scratch/kinds.tsv" -v scalars="$scratch/scalars" '
function isdig(c) { return (c >= "0" && c <= "9") }
function luhn(d,   n, i, sum, dbl, dig) {
  n = length(d); sum = 0; dbl = 0
  for (i = n; i >= 1; i--) {
    dig = substr(d, i, 1) + 0
    if (dbl) { dig *= 2; if (dig > 9) dig -= 9 }
    sum += dig
    dbl = !dbl
  }
  return (sum % 10) == 0
}
function addc(st, en, kd, val) {
  nc++; cst[nc] = st; cen[nc] = en; ckd[nc] = kd; cval[nc] = val
}
function before(s1, e1, k1, s2, e2, k2) {
  if (s1 != s2) return s1 < s2
  if ((e1 - s1) != (e2 - s2)) return (e1 - s1) > (e2 - s2)
  return k1 < k2
}
function sortcands(   i, j, ts, te, tk, tv) {
  for (i = 2; i <= nc; i++) {
    ts = cst[i]; te = cen[i]; tk = ckd[i]; tv = cval[i]
    j = i - 1
    while (j >= 1 && before(ts, te, tk, cst[j], cen[j], ckd[j])) {
      cst[j + 1] = cst[j]; cen[j + 1] = cen[j]; ckd[j + 1] = ckd[j]; cval[j + 1] = cval[j]
      j--
    }
    cst[j + 1] = ts; cen[j + 1] = te; ckd[j + 1] = tk; cval[j + 1] = tv
  }
}
{
  if ($0 ~ /^[ \t\r]*$/) next
  ticket++
  text = $0
  L = length(text)
  nc = 0

  for (i = 1; i <= L; i++) {
    rest = substr(text, i)
    if (match(rest, /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+[.][A-Za-z][A-Za-z]+/))
      addc(i, i + RLENGTH - 1, "email", substr(rest, 1, RLENGTH))
  }

  for (i = 1; i <= L; i++) {
    rest = substr(text, i)
    if (!match(rest, /^[0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9]/)) continue
    en = i + RLENGTH - 1
    if (i > 1 && isdig(substr(text, i - 1, 1))) continue
    if (en < L && isdig(substr(text, en + 1, 1))) continue
    v = substr(rest, 1, RLENGTH)
    area = substr(v, 1, 3)
    if (area != "000" && area != "666" && (area + 0) < 900) addc(i, en, "ssn", v)
  }

  for (i = 1; i <= L; i++) {
    rest = substr(text, i)
    if (!match(rest, /^[0-9][0-9]?[0-9]?[.][0-9][0-9]?[0-9]?[.][0-9][0-9]?[0-9]?[.][0-9][0-9]?[0-9]?/)) continue
    en = i + RLENGTH - 1
    v = substr(rest, 1, RLENGTH)
    if (i > 1) { p = substr(text, i - 1, 1); if (isdig(p) || p == ".") continue }
    if (en < L) { q = substr(text, en + 1, 1); if (isdig(q) || q == ".") continue }
    split(v, oct, ".")
    ok = 1
    for (k = 1; k <= 4; k++) if ((oct[k] + 0) > 255) ok = 0
    if (!ok) continue
    o1 = oct[1] + 0; o2 = oct[2] + 0
    if (o1 == 10 || (o1 == 192 && o2 == 168) || (o1 == 172 && o2 >= 16 && o2 <= 31))
      addc(i, en, "private-ip", v)
  }

  i = 1
  while (i <= L) {
    if (!isdig(substr(text, i, 1))) { i++; continue }
    st = i; digits = ""; last = i; j = i
    while (j <= L) {
      cj = substr(text, j, 1)
      if (isdig(cj)) { digits = digits cj; last = j; j++; continue }
      if ((cj == " " || cj == "-") && j + 1 <= L && isdig(substr(text, j + 1, 1))) { j++; continue }
      break
    }
    nd = length(digits)
    if (nd >= 13 && nd <= 19 && luhn(digits)) addc(st, last, "card", substr(text, st, last - st + 1))
    i = last + 1
  }

  for (i = 1; i <= L; i++) {
    ci = substr(text, i, 1)
    if (ci != "+" && !isdig(ci)) continue
    if (i > 1) { p = substr(text, i - 1, 1); if (isdig(p) || p == "+") continue }
    rest = substr(text, i)
    if (!match(rest, /^(\+[0-9][0-9]?[0-9]?[ .-]?)?(\([0-9][0-9][0-9]\)[ .-]?|[0-9][0-9][0-9][ .-]?)[0-9][0-9][0-9][ .-]?[0-9][0-9][0-9][0-9]/)) continue
    en = i + RLENGTH - 1
    if (en < L && isdig(substr(text, en + 1, 1))) continue
    v = substr(rest, 1, RLENGTH)
    if (v !~ /[ .(-]/ && substr(v, 1, 1) != "+") continue
    addc(i, en, "phone", v)
  }

  sortcands()
  lastend = 0
  for (k = 1; k <= nc; k++) {
    if (cst[k] < lastend) continue
    lastend = cen[k]
    printf "%d,%d,%s,%s\n", ticket, ticket, ckd[k], cval[k] >> rows
    findings++
    kind[ckd[k]]++
    if (!(cval[k] in uniq)) { uniq[cval[k]] = 1; uniqn++ }
    if (ticket != lastflag) { flagged++; lastflag = ticket }
  }
}
END {
  for (k in kind) printf "%s\t%d\n", k, kind[k] > kinds
  printf "%d %d %d %d\n", ticket, findings, flagged, uniqn > scalars
}' "$src"

{
  printf 'ticket,line,kind,value\n'
  cat "$scratch/rows.csv"
} > "$outdir/findings.csv"

read -r tickets findings flagged uniqn < "$scratch/scalars"
by_kind=$(sort -t$'\t' -k1,1 "$scratch/kinds.tsv" 2>/dev/null | awk -F'\t' '
  BEGIN { sep = "" }
  { printf "%s\"%s\":%d", sep, $1, $2; sep = "," }
')
printf '{"by_kind":{%s},"findings":%d,"tickets":%d,"tickets_flagged":%d,"unique_values":%d}\n' \
  "$by_kind" "$findings" "$tickets" "$flagged" "$uniqn" > "$outdir/summary.json"

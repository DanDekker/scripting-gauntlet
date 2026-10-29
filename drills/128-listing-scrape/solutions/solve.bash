#!/usr/bin/env bash
# 128-listing-scrape - split the markup into one tag per line, then one awk pass.
# awk keeps a stack of open <div>s so a nested item does not steal the outer item's
# fields; the innermost item owns the elements it contains.
set -euo pipefail
export LC_ALL=C

inp="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
page="$inp/page.html"
[[ -r "$page" ]] || { echo "missing $page" >&2; exit 1; }
mkdir -p "$outdir"

tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

# One token per line: every `<` and every `>` starts a new line, so tags and the text
# between them never share a line. Newlines inside a name become plain whitespace later.
awk '{ gsub(/</, "\n<"); gsub(/>/, ">\n"); print }' "$page" > "$tmpdir/tokens"

awk -v rowfile="$outdir/items.csv" -v sumfile="$outdir/summary.json" '
function trim(s) { sub(/^[ \t\r\n]+/, "", s); sub(/[ \t\r\n]+$/, "", s); return s }
function repl(s, from, to,   out, i) {
  while ((i = index(s, from)) > 0) { out = out substr(s, 1, i - 1) to; s = substr(s, i + length(from)) }
  return out s
}
function decode(s) {
  s = repl(s, "&#39;", "\047")
  s = repl(s, "&lt;", "<")
  s = repl(s, "&gt;", ">")
  s = repl(s, "&quot;", "\042")
  s = repl(s, "&apos;", "\047")
  s = repl(s, "&amp;", "&")
  return s
}
function collapse(s) { gsub(/[ \t\r\n]+/, " ", s); return trim(s) }
function attrval(tag, want,   i, s, j) {
  i = index(tag, " " want "=\"")
  if (i == 0) return ""
  s = substr(tag, i + length(want) + 3)
  j = index(s, "\"")
  if (j == 0) return ""
  return substr(s, 1, j - 1)
}
function has_token(list, want,   n, parts, i) {
  n = split(list, parts, /[ \t]+/)
  for (i = 1; i <= n; i++) if (parts[i] == want) return 1
  return 0
}
function price_cents(s,   dot, whole, frac) {
  s = trim(s)
  if (substr(s, 1, 1) != "$") return -1
  s = substr(s, 2)
  if (s == "") return -1
  dot = index(s, ".")
  if (dot > 0) {
    whole = substr(s, 1, dot - 1)
    frac = substr(s, dot + 1)
    if (frac !~ /^[0-9]+$/ || length(frac) > 2) return -1
    if (length(frac) == 1) frac = frac "0"
  } else { whole = s; frac = "00" }
  if (whole !~ /^[0-9,]+$/) return -1
  gsub(/,/, "", whole)
  if (whole == "") return -1
  return whole * 100 + frac
}
function fmt(c) { return int(c / 100) "." sprintf("%02d", c % 100) }
function csvfield(s,   out, i, ch) {
  if (s !~ /[",]/) return s
  out = ""
  for (i = 1; i <= length(s); i++) { ch = substr(s, i, 1); out = out (ch == "\"" ? "\"\"" : ch) }
  return "\"" out "\""
}
function close_span() {
  vals[capt_item, capt_field] = collapse(decode(buf))
  capturing = 0
  buf = ""
}
BEGIN {
  sp = 0; cur = 0; nitems = 0; capturing = 0
  print "name,price,link" > rowfile
}
{
  line = $0
  sub(/\r$/, "", line)
  if (line ~ /^[ \t]*$/) next
  if (substr(line, 1, 1) != "<") { if (capturing) buf = buf " " line; next }

  if (substr(line, 1, 2) == "</") {
    tname = substr(line, 3)
    sub(/[ \t>].*$/, "", tname)
    if (tname == "div") { if (sp > 0) cur = stk[sp--] }
    else if (tname == "span" && capturing) close_span()
    next
  }

  tname = substr(line, 2)
  sub(/[ \t>\/].*$/, "", tname)

  if (tname == "div") {
    if (has_token(attrval(line, "class"), "item")) { nitems++; stk[++sp] = cur; cur = nitems }
    else { stk[++sp] = cur }
    next
  }
  if (tname == "span") {
    c = trim(attrval(line, "class"))
    if ((c == "name" || c == "price") && cur > 0 && !fieldset[cur, c]) {
      fieldset[cur, c] = 1
      vals[cur, c] = ""
      capturing = 1
      capt_field = c
      capt_item = cur
      buf = ""
    }
    next
  }
  if (tname == "a") {
    c = trim(attrval(line, "class"))
    if (c == "link" && cur > 0 && !fieldset[cur, "link"]) {
      fieldset[cur, "link"] = 1
      vals[cur, "link"] = trim(decode(attrval(line, "href")))
    }
    next
  }
}
END {
  if (capturing) close_span()
  kept = 0; skipped = 0; dups = 0; priced = 0; total = 0
  for (i = 1; i <= nitems; i++) {
    nm = fieldset[i, "name"] ? vals[i, "name"] : ""
    if (nm == "") { skipped++; continue }
    cents = price_cents(fieldset[i, "price"] ? vals[i, "price"] : "")
    pstr = (cents < 0) ? "" : fmt(cents)
    key = nm SUBSEP pstr
    if (key in seen) { dups++; continue }
    seen[key] = 1
    lnk = fieldset[i, "link"] ? vals[i, "link"] : ""
    print csvfield(nm) "," pstr "," csvfield(lnk) > rowfile
    kept++
    if (cents >= 0) { priced++; total += cents }
  }
  summary = sprintf("{\"items\":%d,\"kept\":%d,\"skipped\":%d,\"duplicates\":%d,\"priced\":%d,\"unpriced\":%d,\"total\":%s}", nitems, kept, skipped, dups, priced, kept - priced, fmt(total))
  print summary > sumfile
}
' "$tmpdir/tokens"

echo "128-listing-scrape: wrote $outdir/items.csv and $outdir/summary.json"

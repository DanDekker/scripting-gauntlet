#!/usr/bin/env bash
# 011-xml-attrs — scoped regex per element, not one regex for the document.
set -euo pipefail

src="${IN:?IN not set}/catalog.xml"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

body=$(mktemp)
trap 'rm -f "$body"' EXIT

awk '
function attr(line, name,   re, s) {
  re = name "=\"[^\"]*\""
  if (match(line, re)) {
    s = substr(line, RSTART, RLENGTH)
    sub(/^[^=]*="/, "", s)
    sub(/"$/, "", s)
    return s
  }
  return ""
}
function elem(line, tag,   re, s) {
  re = "<" tag ">[^<]*</" tag ">"
  if (match(line, re)) {
    s = substr(line, RSTART, RLENGTH)
    sub(/^<[^>]*>/, "", s)
    sub(/<\/[^>]*>$/, "", s)
    return s
  }
  return ""
}
/<product / { pid = attr($0, "id"); price = attr($0, "price"); pname = ""; ptags = ""; next }
/<name>/ { pname = elem($0, "name"); next }
/<tag>/ { t = elem($0, "tag"); ptags = (ptags == "" ? t : ptags "|" t); next }
/<\/product>/ { printf "%s,%s,%s,%s\n", pid, pname, price, ptags; next }
' "$src" | sort -t, -k1,1 > "$body"

{
  printf 'id,name,price,tags\n'
  cat "$body"
} > "$outdir/products.csv"

count=$(wc -l < "$body" | tr -d ' ')
printf '{"products":%s}\n' "$count" > "$outdir/summary.json"

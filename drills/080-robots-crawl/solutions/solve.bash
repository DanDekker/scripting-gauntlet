#!/usr/bin/env bash
# 080-robots-crawl - one awk pass for the rules, one for the URLs.
set -euo pipefail
export LC_ALL=C

inp="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
[[ -r "$inp/robots.txt" && -r "$inp/urls.txt" ]] \
  || { echo "missing robots.txt or urls.txt" >&2; exit 1; }
mkdir -p "$outdir"

rules=$(mktemp)
body=$(mktemp)
trap 'rm -f "$rules" "$body"' EXIT

awk -v rules="$rules" '
function trim(s) { gsub(/^[ \t\r]+|[ \t\r]+$/, "", s); return s }
function flush(   i, a) {
  for (i = 1; i <= nagents; i++) {
    a = agents[i]
    if (a == "scriptbot" || a == "*") printf "%s\t%s\t%s\n", a, ruleallow, rulepat > rules
  }
}
{
  line = $0
  sub(/#.*/, "", line)
  line = trim(line)
  if (line == "") { nagents = 0; inrules = 0; next }
  colon = index(line, ":")
  if (colon == 0) next
  key = tolower(trim(substr(line, 1, colon - 1)))
  value = trim(substr(line, colon + 1))
  if (key == "user-agent") {
    if (inrules) { nagents = 0; inrules = 0 }
    agents[++nagents] = tolower(value)
  } else if (key == "allow" || key == "disallow") {
    inrules = 1
    ruleallow = (key == "allow") ? "1" : "0"
    rulepat = value
    flush()
  }
}' "$inp/robots.txt"

# Prefer the ScriptBot rules; fall back to * only when ScriptBot has none.
if grep -q '^scriptbot' "$rules"; then
  selected=$(mktemp)
  awk -F'\t' '$1 == "scriptbot"' "$rules" > "$selected"
else
  selected=$(mktemp)
  awk -F'\t' '$1 == "*"' "$rules" > "$selected"
fi
trap 'rm -f "$rules" "$body" "$selected"' EXIT

awk -F'\t' -v urls="$inp/urls.txt" -v body="$body" '
function globre(pat,   out, i, ch) {
  out = "^"
  for (i = 1; i <= length(pat); i++) {
    ch = substr(pat, i, 1)
    if (ch == "*") out = out ".*"
    else if (ch == "$" && i == length(pat)) out = out "$"
    else if (index("\\.^$+?()[]{}|", ch)) out = out "\\" ch
    else out = out ch
  }
  return out
}
FNR == NR {
  n++; allow[n] = $2; pat[n] = $3; re[n] = globre($3); len[n] = length($3)
  next
}
BEGIN { while ((getline line < urls) > 0) URL[++nurl] = line; close(urls) }
END {
  for (u = 1; u <= nurl; u++) {
    url = URL[u]; gsub(/^[ \t\r]+|[ \t\r]+$/, "", url)
    if (url == "" || substr(url, 1, 1) == "#") continue
    target = url
    sub(/^[a-zA-Z][a-zA-Z0-9+.-]*:\/\/[^\/]*/, "", target)
    sub(/#.*/, "", target)
    if (target == "") target = "/"
    best = -1; bestallow = 1; bestpat = ""
    for (i = 1; i <= n; i++) {
      if (target !~ re[i]) continue
      if (len[i] > best || (len[i] == best && allow[i] == "1")) {
        best = len[i]; bestallow = allow[i]; bestpat = pat[i]
      }
    }
    printf "%s,%s,%s\n", url, (bestallow == "1" ? "yes" : "no"), bestpat > body
  }
  close(body)
}' "$selected" /dev/null

{
  printf 'url,allowed,rule\n'
  LC_ALL=C sort -t, -k1,1 "$body"
} > "$outdir/crawl.csv"

urls=$(awk 'END { print NR }' "$body")
allowed=$(awk -F, '$2 == "yes"' "$body" | awk 'END { print NR }')
printf '{"urls":%d,"allowed":%d,"disallowed":%d}\n' \
  "$urls" "$allowed" "$((urls - allowed))" > "$outdir/summary.json"

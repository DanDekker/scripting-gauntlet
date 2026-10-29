#!/usr/bin/env bash
# 126-window-split - awk packs paragraphs into character-budget windows.
set -euo pipefail
export LC_ALL=C

indir="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"
for f in doc.txt config.json; do
  [[ -f "$indir/$f" ]] || { echo "missing $indir/$f" >&2; exit 1; }
done
command -v jq >/dev/null || { echo "jq is required" >&2; exit 1; }

max=$(jq -er '.max_chars' "$indir/config.json")
overlap=$(jq -er '.overlap' "$indir/config.json")
[[ "$max" =~ ^[0-9]+$ ]] && (( max > 0 )) || { echo "config.json: max_chars must be positive" >&2; exit 1; }
[[ "$overlap" =~ ^[0-9]+$ ]] || { echo "config.json: overlap must be a non-negative integer" >&2; exit 1; }

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

awk -v max="$max" -v overlap="$overlap" -v rows="$scratch/rows.csv" -v scalars="$scratch/scalars" -v extra="$scratch/extra" '
function trim(s) { sub(/^[ \t\r]+/, "", s); sub(/[ \t\r]+$/, "", s); return s }
function joinparts(k,   s, i) {
  s = part[1]
  for (i = 2; i <= k; i++) s = s "\n\n" part[i]
  return s
}
function tail(t,   s, n) {
  if (overlap <= 0) return ""
  n = length(t)
  s = (n > overlap) ? substr(t, n - overlap + 1) : t
  n = length(s)
  if (n > max) s = substr(s, n - max + 1)
  return s
}
function esc(t,   out, i, n, c) {
  out = ""; n = length(t)
  for (i = 1; i <= n; i++) {
    c = substr(t, i, 1)
    if (c == "\\") out = out "\\\\"
    else if (c == "\n") out = out "\\n"
    else if (c == "\"") out = out "\"\""
    else out = out c
  }
  return out
}
{
  line = $0
  sub(/[ \t\r]+$/, "", line)
  if (trim($0) == "") {
    if (cur != "") { np++; para[np] = cur; cur = "" }
    next
  }
  cur = (cur == "") ? line : cur "\n" line
}
END {
  if (cur != "") { np++; para[np] = cur }
  kept = 0
  for (i = 1; i <= np; i++) {
    p = trim(para[i])
    if (p != "") { kept++; para[kept] = p }
  }
  np = kept

  pref = ""; i = 1; nw = 0
  while (i <= np) {
    p = para[i]
    if (pref != "" && (length(pref) + 2 + length(p)) > max) pref = ""
    if (length(p) > max) {
      at = 0
      while (at < length(p)) {
        piece = substr(p, at + 1, max)
        nw++; win[nw] = piece
        at += max
      }
      i++
      pref = tail(win[nw])
      continue
    }
    k = 0
    if (pref != "") { k++; part[k] = pref }
    k++; part[k] = p
    i++
    while (i <= np) {
      part[k + 1] = para[i]
      if (length(joinparts(k + 1)) <= max) { k++; i++ } else break
    }
    nw++; win[nw] = joinparts(k)
    pref = tail(win[nw])
  }

  total = 0; biggest = 0
  for (j = 1; j <= nw; j++) {
    len = length(win[j])
    printf "%d,%d,\"%s\"\n", j, len, esc(win[j]) >> rows
    total += len
    if (len > biggest) biggest = len
  }
  printf "%d %d %d\n", np, nw, total > scalars
  printf "%d\n", biggest > extra
}
' "$indir/doc.txt"

{
  printf 'index,chars,text\n'
  cat "$scratch/rows.csv"
} > "$outdir/windows.csv"

read -r paragraphs windows chars < "$scratch/scalars"
read -r max_window < "$scratch/extra"
printf '{"chars":%d,"max_window":%d,"overlap":%d,"paragraphs":%d,"windows":%d}\n' \
  "$chars" "$max_window" "$overlap" "$paragraphs" "$windows" > "$outdir/summary.json"

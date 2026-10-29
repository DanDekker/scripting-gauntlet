#!/usr/bin/env bash
# Run the review checklist over a unified diff with awk: one rule per check, one row per
# (file, diff line, code).
set -euo pipefail

src="${IN:?IN not set}/changes.diff"
out_dir="${OUT:?OUT not set}"
mkdir -p "$out_dir"
[[ -f $src ]] || { echo "missing $src" >&2; exit 1; }

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

awk -v counts="$scratch/counts" '
function is_ipv4(text,   n, runs, i, groups, k, ok) {
  n = split(text, runs, /[^0-9.]+/)
  for (i = 1; i <= n; i++) {
    if (runs[i] == "") continue
    if (split(runs[i], groups, /\./) != 4) continue
    ok = 1
    for (k = 1; k <= 4; k++) {
      if (groups[k] !~ /^[0-9][0-9]?[0-9]?$/ || groups[k] + 0 > 255) { ok = 0; break }
    }
    if (ok) return 1
  }
  return 0
}

function finding(code) { printf "%d\t%s\t%s\n", NR, file, code }

/^diff --git / {
  header = $0
  sub(/^diff --git a\//, "", header)
  cut = index(header, " b/")
  file = (cut > 0) ? substr(header, cut + 3) : header
  if (!(file in seen)) { seen[file] = 1; files++ }
  next
}

/^\+\+\+ / {
  side = substr($0, 5)
  if (side != "/dev/null") { sub(/^b\//, "", side); file = side }
  next
}

/^\+/ {
  added++
  body = substr($0, 2)
  if (substr($0, length($0), 1) == " " || substr($0, length($0), 1) == "\t") finding("trailing-whitespace")
  if (length($0) > 100) finding("long-line")
  if (index(body, "TODO") > 0 || index(body, "FIXME") > 0) finding("todo")
  if (index(body, "console.log") > 0 || index(body, "print(") > 0) finding("debug")
  if (index(body, "http://") > 0 || index(body, "https://") > 0 || is_ipv4(body)) finding("hardcoded-endpoint")
  next
}

END { printf "%d\t%d\n", files, added > counts }
' "$src" > "$scratch/findings.tsv"

IFS=$'\t' read -r files lines_added < "$scratch/counts"

LC_ALL=C sort -t$'\t' -k2,2 -k1,1n -k3,3 "$scratch/findings.tsv" > "$scratch/sorted.tsv"

{
  printf 'file,line,code\n'
  awk -F'\t' '{ printf "%s,%s,%s\n", $2, $1, $3 }' "$scratch/sorted.tsv"
} > "$out_dir/findings.csv"

findings=$(wc -l < "$scratch/sorted.tsv" | tr -d ' ')
flagged=$(cut -f2 "$scratch/sorted.tsv" | LC_ALL=C sort -u | wc -l | tr -d ' ')
by_code=$(awk -F'\t' '
  { count[$3]++ }
  END {
    n = split("debug hardcoded-endpoint long-line todo trailing-whitespace", codes, " ")
    out = ""
    for (i = 1; i <= n; i++) {
      if (codes[i] in count) out = out (out == "" ? "" : ",") "\"" codes[i] "\":" count[codes[i]]
    }
    print "{" out "}"
  }
' "$scratch/sorted.tsv")

printf '{"files":%d,"lines_added":%d,"findings":%d,"by_code":%s,"files_flagged":%d}\n' \
  "$files" "$lines_added" "$findings" "$by_code" "$flagged" > "$out_dir/summary.json"

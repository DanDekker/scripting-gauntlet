#!/usr/bin/env bash
# Fill a {{template}} with awk (line-scoped scanning) + jq (JSON value rendering).
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

values="$in_dir/values.json"
template="$in_dir/template.txt"

# name<TAB>rendered-text: strings verbatim, arrays/objects compact JSON, scalars JSON text.
jq -r 'to_entries[]
       | .key + "\t" + (.value
         | if type == "string" then .
           elif (type == "array" or type == "object") then tojson
           else tostring end)' "$values" > "$scratch/values.tsv"

awk -v vfile="$scratch/values.tsv" -v counts="$scratch/counts" -v refs="$scratch/refs" '
function trim(s) { gsub(/^[ \t]+/, "", s); gsub(/[ \t]+$/, "", s); return s }
BEGIN {
  while ((getline vline < vfile) > 0) {
    cut = index(vline, "\t")
    values[substr(vline, 1, cut - 1)] = substr(vline, cut + 1)
    have[substr(vline, 1, cut - 1)] = 1
  }
  close(vfile)
  np = 0; nd = 0; nh = 0; ndef = 0
}
{
  if (FNR > 1) printf "\n"
  line = $0
  n = length(line)
  i = 1
  out = ""
  while (i <= n) {
    p = index(substr(line, i), "{{")
    if (p == 0) { out = out substr(line, i); break }
    start = i + p - 1
    out = out substr(line, i, p - 1)
    rest = substr(line, start)
    q = index(rest, "}}")
    if (q == 0) { out = out rest; break }
    inside = substr(rest, 3, q - 3)
    bar = index(inside, "|")
    if (bar > 0) {
      left = substr(inside, 1, bar - 1)
      right = trim(substr(inside, bar + 1))
      hasdef = 1
    } else {
      left = inside; right = ""; hasdef = 0
    }
    name = trim(left)
    if (name !~ /^[A-Za-z0-9_.-]+$/) {   # {{}} or {{a b}}: not a placeholder
      out = out "{{"
      i = start + 2
      continue
    }
    np++
    if (!(name in seen)) { seen[name] = 1; nd++ }
    referenced[name] = 1
    if (name in have) {
      out = out values[name]
    } else if (hasdef) {
      out = out right
      ndef++
    } else {
      out = out "[MISSING:" name "]"
      nh++
    }
    i = start + q + 1
  }
  printf "%s", out
}
END {
  printf "placeholders\t%d\ndistinct\t%d\nholes\t%d\ndefaults_used\t%d\n", np, nd, nh, ndef > counts
  for (k in referenced) print k > refs
  close(counts); close(refs)
}
' "$template" > "$scratch/rendered"

# The rendered file ends with a newline iff the template did.
if [ -s "$template" ] && [ -z "$(tail -c 1 "$template")" ]; then
  printf '\n' >> "$scratch/rendered"
fi
mv "$scratch/rendered" "$out_dir/rendered.txt"

read_field() { awk -F'\t' -v k="$1" '$1 == k { print $2 }' "$scratch/counts"; }
placeholders=$(read_field placeholders)
distinct=$(read_field distinct)
holes=$(read_field holes)
defaults_used=$(read_field defaults_used)

jq -r 'keys[]' "$values" | LC_ALL=C sort > "$scratch/keys"
if [ -s "$scratch/refs" ]; then
  LC_ALL=C sort -u "$scratch/refs" > "$scratch/refs.sorted"
else
  : > "$scratch/refs.sorted"
fi
comm -23 "$scratch/keys" "$scratch/refs.sorted" > "$scratch/unused"
unused_json=$(jq -R -s 'split("\n") | map(select(length > 0))' "$scratch/unused")

jq -n \
  --argjson placeholders "$placeholders" \
  --argjson distinct "$distinct" \
  --argjson holes "$holes" \
  --argjson unused "$unused_json" \
  --argjson defaults_used "$defaults_used" \
  '{placeholders: $placeholders,
    distinct: $distinct,
    holes: $holes,
    unused: $unused,
    defaults_used: $defaults_used}' > "$out_dir/summary.json"

#!/usr/bin/env bash
# Scan a tree for credentials: awk finds candidates, the same pass drops the noise.
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
tree="$in_dir/tree"
mkdir -p "$out_dir"

if [ ! -d "$tree" ]; then
  echo "no such directory: $tree" >&2
  exit 1
fi

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

find "$tree" -type f | LC_ALL=C sort > "$scratch/files.txt"

files_scanned=$(awk 'END { print NR }' "$scratch/files.txt")
sample_files=$(awk -v prefix="$tree/" '
  { relative = substr($0, length(prefix) + 1) }
  relative ~ /\.example(\.txt)?$/ { n++ }
  END { print n + 0 }
' "$scratch/files.txt")

: > "$scratch/hits.tsv"
while IFS= read -r file; do
  relative=${file#"$tree"/}
  case "$relative" in
    *.example | *.example.txt) sample=1 ;;
    *) sample=0 ;;
  esac
  LC_ALL=C awk -v file="$relative" -v sample="$sample" '
    {
      line = $0
      sub(/\r$/, "", line)
      low = tolower(line)
      if (!match(low, /(api_key|apikey|secret|password|passwd|token)[ \t]*[:=]/)) next
      key = substr(line, RSTART, RLENGTH)
      sub(/[ \t]*[:=]$/, "", key)
      value = substr(line, RSTART + RLENGTH)
      sub(/^[ \t]+/, "", value)
      if (value ~ /^["\047]/) {
        quote = substr(value, 1, 1)
        body = substr(value, 2)
        cut = index(body, quote)
        value = (cut > 0 ? substr(body, 1, cut - 1) : body)
      } else {
        sub(/[ \t].*$/, "", value)
      }
      printf "C\t%s\t%d\t%s\t%s\n", file, NR, key, value
      if (sample) next
      if (value == "") next
      lowered = tolower(value)
      if (lowered == "changeme" || lowered == "your-key-here" || lowered == "xxx" || \
          lowered == "todo" || lowered == "example" || lowered == "<redacted>") next
      if (length(value) < 8) next
      printf "S\t%s\t%d\t%s\t%s\n", file, NR, key, value
    }
  ' "$file" >> "$scratch/hits.tsv"
done < "$scratch/files.txt"

candidates=$(awk -F'\t' '$1 == "C" { n++ } END { print n + 0 }' "$scratch/hits.tsv")
secrets=$(awk -F'\t' '$1 == "S" { n++ } END { print n + 0 }' "$scratch/hits.tsv")
unique_values=$(awk -F'\t' '$1 == "S" { print $5 }' "$scratch/hits.tsv" | LC_ALL=C sort -u | awk 'END { print NR }')

{
  printf 'file,line,key,value\n'
  awk -F'\t' '$1 == "S" { printf "%s\t%s\t%s\t%s\n", $2, $3, $4, $5 }' "$scratch/hits.tsv" \
    | LC_ALL=C sort -t$'\t' -k1,1 -k2,2n \
    | awk -F'\t' 'function q(s) {
        if (index(s, ",") || index(s, "\"")) {
          gsub(/"/, "\"\"", s)
          return "\"" s "\""
        }
        return s
      }
      { printf "%s,%s,%s,%s\n", q($1), $2, q($3), q($4) }'
} > "$out_dir/findings.csv"

jq -n \
  --argjson files_scanned "$files_scanned" \
  --argjson candidates "$candidates" \
  --argjson secrets "$secrets" \
  --argjson unique_values "$unique_values" \
  --argjson sample_files "$sample_files" \
  '{files_scanned: $files_scanned, candidates: $candidates, secrets: $secrets,
    unique_values: $unique_values, sample_files: $sample_files}' > "$out_dir/summary.json"

#!/usr/bin/env bash
# Triage a unified diff with awk. Every risk flag is collected per file, then the
# flag list is emitted in a fixed (alphabetical) order.
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"

records=$(awk '
  /^diff --git / {
    if (path != "") emit()
    path = ""; added = 0; deleted = 0; binary = 0; isnew = 0; isdel = 0; mode = 0; secret = 0
    header = $0
    sub(/^diff --git a\//, "", header)
    idx = index(header, " b/")
    if (idx > 0) path = substr(header, 1, idx - 1)
    next
  }
  /^Binary files / { binary = 1; next }
  /^new file mode / { isnew = 1; next }
  /^deleted file mode / { isdel = 1; next }
  /^old mode / { mode = 1; next }
  /^new mode / { mode = 1; next }
  /^--- / { if ($0 == "--- /dev/null") isnew = 1; next }
  /^\+\+\+ / {
    side = substr($0, 5)
    if (side == "/dev/null") isdel = 1
    else { sub(/^b\//, "", side); path = side }
    next
  }
  /^\+/ {
    added++
    line = tolower($0)
    if (index(line, "api_key") || index(line, "api-key") || index(line, "password") || \
       index(line, "secret") || index(line, "-----begin")) secret = 1
    next
  }
  /^-/ { deleted++; next }
  END { if (path != "") emit() }

  function emit(   flags, sep, n) {
    flags = ""
    if (binary) { flags = flags "binary" }
    if (isdel) { sep = (flags == "" ? "" : ";"); flags = flags sep "deleted" }
    n = added + deleted
    if (n >= 100) { sep = (flags == "" ? "" : ";"); flags = flags sep "large" }
    if (mode) { sep = (flags == "" ? "" : ";"); flags = flags sep "mode-change" }
    if (isnew) { sep = (flags == "" ? "" : ";"); flags = flags sep "new" }
    if (secret) { sep = (flags == "" ? "" : ";"); flags = flags sep "secret" }
    print path "\t" added "\t" deleted "\t" flags
  }
' "$in_dir/changes.diff")

{
  printf 'path,added,deleted,flags\n'
  printf '%s\n' "$records" | awk -F'\t' '
    { print $1 "," $2 "," $3 "," $4 }
  ' | LC_ALL=C sort -t, -k1,1
} > "$out_dir/risk.csv"

files=$(($(wc -l < "$out_dir/risk.csv") - 1))
total_added=$(awk -F, 'NR > 1 { s += $2 } END { print s + 0 }' "$out_dir/risk.csv")
total_deleted=$(awk -F, 'NR > 1 { s += $3 } END { print s + 0 }' "$out_dir/risk.csv")
flagged=$(awk -F, 'NR > 1 && $4 != "" { c++ } END { print c + 0 }' "$out_dir/risk.csv")
top_risk=$(awk -F, 'NR > 1 {
  n = ($4 == "" ? 0 : split($4, parts, ";"))
  if (n > best || (n == best && (bestp == "" || $1 < bestp))) { best = n; bestp = $1 }
} END { print (best > 0 ? bestp : "") }' "$out_dir/risk.csv")

jq -n \
  --argjson files "$files" \
  --argjson total_added "$total_added" \
  --argjson total_deleted "$total_deleted" \
  --argjson flagged "$flagged" \
  --arg top_risk "$top_risk" \
  '{files: $files, total_added: $total_added, total_deleted: $total_deleted,
    flagged_files: $flagged, top_risk: $top_risk}' > "$out_dir/summary.json"

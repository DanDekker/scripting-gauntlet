#!/usr/bin/env bash
# Check claim support with awk: squash whitespace, lowercase, then substring containment.
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

for f in answer.md sources.txt; do
  [ -f "$in_dir/$f" ] || { printf 'missing %s/%s\n' "$in_dir" "$f" >&2; exit 1; }
 done

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

awk -v csv="$scratch/claims.csv" -v js="$scratch/summary.json" '
function trim(s) { sub(/^[ \t]+/, "", s); sub(/[ \t]+$/, "", s); return s }
function squash(s) { s = trim(s); gsub(/[ \t]+/, " ", s); return tolower(s) }
function q(s,   t) {
  if (index(s, ",") || index(s, "\"")) {
    t = s
    gsub(/"/, "\"\"", t)
    return "\"" t "\""
  }
  return s
}
FILENAME == ARGV[1] {
  s = squash($0)
  if (s != "") { ns++; src[ns] = s }
  next
}
{
  t = trim($0)
  if (t ~ /^Claim:/) {
    numbered = 0
    text = trim(substr(t, 7))
    num = 0
  } else if (match(t, /^Claim[ \t]+[0-9]+:/)) {
    numbered = 1
    head = substr(t, 1, RLENGTH)
    text = trim(substr(t, RLENGTH + 1))
    sub(/^Claim[ \t]+/, "", head)
    sub(/:$/, "", head)
    num = head + 0
  } else next
  n++
  ord[n] = n
  nnum[n] = (numbered ? num : n)
  tx[n] = text
  needle = squash(text)
  sup = 0
  if (needle != "") {
    for (i = 1; i <= ns; i++) if (index(src[i], needle) > 0) { sup = 1; break }
  }
  sx[n] = sup
}
END {
  for (i = 2; i <= n; i++) {
    k = nnum[i]; o = ord[i]; s = sx[i]; tt = tx[i]; j = i - 1
    while (j >= 1 && (nnum[j] > k || (nnum[j] == k && ord[j] > o))) {
      nnum[j + 1] = nnum[j]; ord[j + 1] = ord[j]; sx[j + 1] = sx[j]; tx[j + 1] = tx[j]
      j--
    }
    nnum[j + 1] = k; ord[j + 1] = o; sx[j + 1] = s; tx[j + 1] = tt
  }

  printf "number,supported,text\n" > csv
  ok = 0
  for (i = 1; i <= n; i++) {
    if (sx[i]) ok++
    printf "%d,%s,%s\n", nnum[i], (sx[i] ? "true" : "false"), q(tx[i]) > csv
  }
  close(csv)

  m = 0
  for (i = 1; i <= n; i++)
    if (!sx[i] && (m == 0 || nums[m] != nnum[i])) { m++; nums[m] = nnum[i] }

  printf "{\n" > js
  printf "  \"claims\": %d,\n", n > js
  printf "  \"supported\": %d,\n", ok > js
  printf "  \"unsupported\": %d,\n", n - ok > js
  printf "  \"sources\": %d,\n", ns > js
  if (m == 0) {
    printf "  \"unsupported_numbers\": []\n" > js
  } else {
    printf "  \"unsupported_numbers\": [\n" > js
    for (i = 1; i <= m; i++) printf "    %d%s\n", nums[i], (i < m ? "," : "") > js
    printf "  ]\n" > js
  }
  printf "}\n" > js
  close(js)
}
' "$in_dir/sources.txt" "$in_dir/answer.md"

cp "$scratch/claims.csv" "$out_dir/claims.csv"
cp "$scratch/summary.json" "$out_dir/summary.json"

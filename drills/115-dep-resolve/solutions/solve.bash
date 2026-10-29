#!/usr/bin/env bash
# Resolve requirements against installed.txt: awk parses and compares versions.
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

# name<TAB>version, first occurrence wins.
awk '
  {
    line = $0
    sub(/\r$/, "", line)
    if (line ~ /^[ \t]*#/) next
    n = split(line, f, /[ \t]+/)
    if (n < 2) next
    if (f[1] in seen) next
    seen[f[1]] = 1
    print f[1] "\t" f[2]
  }
' "$in_dir/installed.txt" > "$scratch/installed.tsv"

# name<TAB>specifier text, first occurrence wins; markers/comments dropped.
awk '
  {
    line = $0
    sub(/\r$/, "", line)
    t = line
    gsub(/^[ \t]+/, "", t)
    gsub(/[ \t]+$/, "", t)
    if (t == "") next
    if (substr(t, 1, 1) == "#") next
    if (index(t, ";") > 0) next
    cut = index(t, "#")
    if (cut > 0) t = substr(t, 1, cut - 1)
    gsub(/^[ \t]+/, "", t)
    gsub(/[ \t]+$/, "", t)
    if (t == "") next
    if (match(t, /^[A-Za-z0-9_.-]+/) == 0) next
    name = substr(t, 1, RLENGTH)
    rest = substr(t, RLENGTH + 1)
    if (substr(rest, 1, 1) == "[") {
      close_bracket = index(rest, "]")
      if (close_bracket == 0) next
      rest = substr(rest, close_bracket + 1)
    }
    spec = rest
    gsub(/^[ \t]+/, "", spec)
    gsub(/[ \t]+$/, "", spec)
    if (name in seen) next
    seen[name] = 1
    print name "\t" spec
  }
' "$in_dir/requirements.txt" > "$scratch/reqs.tsv"

spec_matches() {
  awk -v spec="$1" -v ver="$2" '
    function cmpver(a, b,   A, B, n, m, i, x, y) {
      n = split(a, A, "."); m = split(b, B, ".")
      for (i = 1; i <= (n > m ? n : m); i++) {
        x = (i <= n) ? (A[i] + 0) : 0
        y = (i <= m) ? (B[i] + 0) : 0
        if (x < y) return -1
        if (x > y) return 1
      }
      return 0
    }
    function prefixmatch(pre, ver,   P, V, n, m, i) {
      n = split(pre, P, "."); m = split(ver, V, ".")
      if (m < n) return 0
      for (i = 1; i <= n; i++) if ((P[i] + 0) != (V[i] + 0)) return 0
      return 1
    }
    function specmatch(set, ver,   n, parts, i, s, op, val, star, pre, Q, n2, i2) {
      n = split(set, parts, ",")
      for (i = 1; i <= n; i++) {
        s = parts[i]
        gsub(/^[ \t]+/, "", s)
        gsub(/[ \t]+$/, "", s)
        if (s == "") continue
        if (substr(s, 1, 2) == "==") { op = "=="; val = substr(s, 3) }
        else if (substr(s, 1, 2) == "!=") { op = "!="; val = substr(s, 3) }
        else if (substr(s, 1, 2) == ">=") { op = ">="; val = substr(s, 3) }
        else if (substr(s, 1, 2) == "<=") { op = "<="; val = substr(s, 3) }
        else if (substr(s, 1, 2) == "~=") { op = "~="; val = substr(s, 3) }
        else if (substr(s, 1, 1) == ">") { op = ">"; val = substr(s, 2) }
        else if (substr(s, 1, 1) == "<") { op = "<"; val = substr(s, 2) }
        else return 0
        gsub(/^[ \t]+/, "", val)
        gsub(/[ \t]+$/, "", val)
        star = 0
        if (length(val) > 2 && substr(val, length(val) - 1) == ".*") {
          star = 1
          val = substr(val, 1, length(val) - 2)
        }
        if (op == "==") {
          if (star) { if (!prefixmatch(val, ver)) return 0 }
          else if (cmpver(val, ver) != 0) return 0
        } else if (op == "!=") {
          if (star) { if (prefixmatch(val, ver)) return 0 }
          else if (cmpver(val, ver) == 0) return 0
        } else if (op == ">=") {
          if (cmpver(ver, val) < 0) return 0
        } else if (op == ">") {
          if (cmpver(ver, val) <= 0) return 0
        } else if (op == "<=") {
          if (cmpver(ver, val) > 0) return 0
        } else if (op == "<") {
          if (cmpver(ver, val) >= 0) return 0
        } else if (op == "~=") {
          if (cmpver(ver, val) < 0) return 0
          n2 = split(val, Q, ".")
          pre = ""
          for (i2 = 1; i2 < n2; i2++) pre = pre (i2 > 1 ? "." : "") Q[i2]
          if (pre != "" && !prefixmatch(pre, ver)) return 0
        }
      }
      return 1
    }
    BEGIN { exit (specmatch(spec, ver) ? 0 : 1) }
  '
}

csv_field() {
  local value=$1
  if [[ $value == *","* || $value == *"\""* ]]; then
    printf '"%s"' "${value//\"/\"\"}"
  else
    printf '%s' "$value"
  fi
}

: > "$scratch/rows.tsv"
satisfied=0
conflicted=0
missing=0
requirements=0

while IFS=$'\t' read -r name spec; do
  [ -z "$name" ] && continue
  spec=${spec-}
  requirements=$((requirements + 1))
  version=$(awk -F'\t' -v n="$name" '$1 == n { print $2; exit }' "$scratch/installed.tsv")
  if [ -z "$version" ]; then
    status=missing
    missing=$((missing + 1))
  elif [ -z "$spec" ] || spec_matches "$spec" "$version"; then
    status=satisfied
    satisfied=$((satisfied + 1))
  else
    status=conflicted
    conflicted=$((conflicted + 1))
  fi
  printf '%s\x1f%s\x1f%s\x1f%s\n' "$name" "$status" "$version" "$spec" >> "$scratch/rows.tsv"
done < "$scratch/reqs.tsv"

: > "$scratch/installed.names"
while IFS=$'\t' read -r name _; do
  [ -n "$name" ] && printf '%s\n' "$name" >> "$scratch/installed.names"
done < "$scratch/installed.tsv"
LC_ALL=C sort -u "$scratch/installed.names" > "$scratch/installed.sorted"
awk -F'\t' '{ print $1 }' "$scratch/reqs.tsv" | LC_ALL=C sort -u > "$scratch/reqs.sorted"
comm -23 "$scratch/installed.sorted" "$scratch/reqs.sorted" > "$scratch/extras"
extra=$(wc -l < "$scratch/extras" | tr -d ' ')
extras_json=$(jq -R -s 'split("\n") | map(select(length > 0))' "$scratch/extras")

{
  printf 'name,status,installed,required\n'
  LC_ALL=C sort -t "$(printf '\x1f')" -k1,1 "$scratch/rows.tsv" |
    while IFS=$'\x1f' read -r name status version spec; do
      printf '%s,%s,%s,%s\n' "$name" "$status" "$(csv_field "${version-}")" "$(csv_field "${spec-}")"
    done
} > "$out_dir/deps.csv"

jq -n \
  --argjson requirements "$requirements" \
  --argjson satisfied "$satisfied" \
  --argjson conflicted "$conflicted" \
  --argjson missing "$missing" \
  --argjson extra "$extra" \
  --argjson extras "$extras_json" \
  '{requirements: $requirements,
    satisfied: $satisfied,
    conflicted: $conflicted,
    missing: $missing,
    extra: $extra,
    extras: $extras}' > "$out_dir/summary.json"

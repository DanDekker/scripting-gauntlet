#!/usr/bin/env bash
# Classify every inline markdown link: awk extracts targets and anchors, coreutils resolves.
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"
docs="$in_dir/docs"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

trim() {
  local s=$1
  s="${s#"${s%%[![:space:]]*}"}"
  s="${s%"${s##*[![:space:]]}"}"
  printf '%s' "$s"
}

# Collapse '.' and '..' in "base/rel" and print the result.
normpath() {
  awk -v base="$1" -v rel="$2" 'BEGIN {
    n = split(base "/" rel, p, "/"); k = 0
    for (i = 1; i <= n; i++) {
      if (p[i] == "" || p[i] == ".") continue
      if (p[i] == "..") {
        if (k > 0 && o[k] != "..") k--
        else o[++k] = ".."
      } else {
        o[++k] = p[i]
      }
    }
    s = ""
    for (i = 1; i <= k; i++) s = s (i > 1 ? "/" : "") o[i]
    print s
  }'
}

# ATX headings of one file -> anchors, one per line.
anchors_for() {
  awk '
    {
      line = $0
      sub(/\r$/, "", line)
      if (line !~ /^#+ /) next
      h = index(line, " ") - 1
      if (h < 1 || h > 6) next
      text = substr(line, h + 1)
      gsub(/^[ \t]+/, "", text)
      gsub(/[ \t]+$/, "", text)
      if (text == "") next
      a = tolower(text)
      gsub(/[^a-z0-9]+/, "-", a)
      sub(/^-+/, "", a)
      sub(/-+$/, "", a)
      print a
    }
  ' "$1"
}

find "$docs" -type f -name '*.md' | LC_ALL=C sort > "$scratch/files.raw"
: > "$scratch/files"
while IFS= read -r absolute; do
  printf '%s\n' "${absolute#"$docs"/}" >> "$scratch/files"
done < "$scratch/files.raw"

while IFS= read -r rel; do
  anchors_for "$docs/$rel" > "$scratch/a.${rel//\//%}"
done < "$scratch/files"

: > "$scratch/rows"
ok=0
broken=0
missing_anchor=0
empty=0
external=0

while IFS= read -r rel; do
  slug=${rel//\//%}
  awk '
    BEGIN { infence = 0 }
    {
      l = $0
      t = l
      sub(/\r$/, "", t)
      gsub(/^[ \t]+/, "", t)
      gsub(/[ \t]+$/, "", t)
      if (substr(t, 1, 3) == "```" || substr(t, 1, 3) == "~~~") { infence = !infence; next }
      if (infence) next
      pos = 1
      while ((i = index(substr(l, pos), "](")) > 0) {
        start = pos + i + 1
        rest = substr(l, start)
        q = index(rest, ")")
        if (q == 0) break
        print FNR "\t" substr(rest, 1, q - 1)
        pos = start + q
      }
    }
  ' "$docs/$rel" > "$scratch/links.tsv"

  while IFS=$'\t' read -r lineno target; do
    target=$(trim "${target-}")
    if [ -z "$target" ]; then
      status=empty
    elif [ "${target:0:7}" = "http://" ] || [ "${target:0:8}" = "https://" ] || [ "${target:0:7}" = "mailto:" ]; then
      external=$((external + 1))
      continue
    else
      path=${target%%#*}
      frag=""
      case "$target" in
        *"#"*) frag=${target#*#} ;;
      esac
      if [ -z "$path" ]; then
        if [ -s "$scratch/a.$slug" ] && grep -Fxq -- "$frag" "$scratch/a.$slug"; then
          status=ok
        else
          status=missing-anchor
        fi
      else
        path=${path//%20/ }
        resolved=$(normpath "$(dirname "$rel")" "$path")
        if [ ! -e "$docs/$resolved" ]; then
          status=broken
        elif [ -z "$frag" ]; then
          status=ok
        else
          target_slug=${resolved//\//%}
          if [ -s "$scratch/a.$target_slug" ] && grep -Fxq -- "$frag" "$scratch/a.$target_slug"; then
            status=ok
          else
            status=missing-anchor
          fi
        fi
      fi
    fi

    case "$status" in
      ok) ok=$((ok + 1)) ;;
      broken) broken=$((broken + 1)) ;;
      missing-anchor) missing_anchor=$((missing_anchor + 1)) ;;
      empty) empty=$((empty + 1)) ;;
    esac
    printf '%s,%s,%s,%s\n' "$rel" "$lineno" "$target" "$status" >> "$scratch/rows"
  done < "$scratch/links.tsv"
done < "$scratch/files"

files=$(wc -l < "$scratch/files" | tr -d ' ')
links=$(wc -l < "$scratch/rows" | tr -d ' ')

{
  printf 'file,line,target,status\n'
  cat "$scratch/rows"
} > "$out_dir/links.csv"

jq -n \
  --argjson files "$files" \
  --argjson links "$links" \
  --argjson ok "$ok" \
  --argjson broken "$broken" \
  --argjson missing_anchor "$missing_anchor" \
  --argjson empty "$empty" \
  --argjson external "$external" \
  '{files: $files,
    links: $links,
    ok: $ok,
    broken: $broken,
    missing_anchor: $missing_anchor,
    empty: $empty,
    external: $external}' > "$out_dir/summary.json"

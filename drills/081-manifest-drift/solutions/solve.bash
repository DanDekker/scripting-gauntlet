#!/usr/bin/env bash
# 081-manifest-drift - old side into a map, new side streamed, removals at the end.
set -euo pipefail
export LC_ALL=C

inp="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
for f in old.json new.json; do
  [[ -r "$inp/$f" ]] || { echo "cannot read $f" >&2; exit 1; }
  jq -e 'type == "array" and all(has("path") and has("bytes") and has("sha256"))' \
    "$inp/$f" >/dev/null || { echo "$f: not a manifest array" >&2; exit 1; }
done
mkdir -p "$outdir"

old=$(mktemp)
new=$(mktemp)
body=$(mktemp)
trap 'rm -f "$old" "$new" "$body"' EXIT

jq -r '.[] | [.path, .bytes, .sha256] | @tsv' "$inp/old.json" | LC_ALL=C sort > "$old"
jq -r '.[] | [.path, .bytes, .sha256] | @tsv' "$inp/new.json" | LC_ALL=C sort > "$new"

awk -F'\t' -v body="$body" -v outdir="$outdir" '
FNR == NR { osize[$1] = $2; osha[$1] = $3; oseen[$1] = 1; next }
{
  nsize[$1] = $2; nsha[$1] = $3; nseen[$1] = 1
}
END {
  for (p in nseen) {
    if (!(p in oseen)) { printf "%s,added,,%s\n", p, nsize[p] > body; added++ }
    else if (osha[p] != nsha[p]) {
      printf "%s,changed,%s,%s\n", p, osize[p], nsize[p] > body; changed++
    } else unchanged++
  }
  for (p in oseen) {
    if (!(p in nseen)) { printf "%s,removed,%s,\n", p, osize[p] > body; removed++ }
  }
  close(body)
  printf "{\"added\":%d,\"removed\":%d,\"changed\":%d,\"unchanged\":%d}\n", \
    added, removed, changed, unchanged > (outdir "/summary.json")
  close(outdir "/summary.json")
}' "$old" "$new"

{
  printf 'path,change,from_bytes,to_bytes\n'
  LC_ALL=C sort -t, -k1,1 "$body"
} > "$outdir/drift.csv"

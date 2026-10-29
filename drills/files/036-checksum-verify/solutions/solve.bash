#!/usr/bin/env bash
# 036-checksum-verify — compare the signed manifest with the tree, then re-sign.
set -euo pipefail

src="${IN:?IN not set}/src"
signed="${IN:?IN not set}/manifest.sha256"
outdir="${OUT:?OUT not set}"
[ -d "$src" ] || { echo "no such directory: $src" >&2; exit 1; }
[ -f "$signed" ] || { echo "no such manifest: $signed" >&2; exit 1; }
mkdir -p "$outdir"

if command -v sha256sum >/dev/null 2>&1; then
  hash_of() { sha256sum "$1" | cut -d' ' -f1; }
elif command -v shasum >/dev/null 2>&1; then
  hash_of() { shasum -a 256 "$1" | cut -d' ' -f1; }
else
  echo "need sha256sum or shasum on PATH" >&2
  exit 1
fi

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

# what is on disk now: <hash> TAB <path relative to src>
while IFS= read -r -d '' file; do
  printf '%s\t%s\n' "$(hash_of "$file")" "${file#"$src"/}"
done < <(find "$src" -type f -print0) | LC_ALL=C sort -t$'\t' -k2,2 > "$work/current.tsv"

# the signed manifest, reshaped to the same TSV: 64 hex, two spaces, path
LC_ALL=C awk 'NF { printf "%s\t%s\n", substr($0, 1, 64), substr($0, 67) }' "$signed" \
  | LC_ALL=C sort -t$'\t' -k2,2 > "$work/signed.tsv"

{
  printf 'path,status,expected,actual\n'
  LC_ALL=C awk -F'\t' -v OFS=',' '
    NR == FNR { current[$2] = $1; next }
    {
      path = $2; expected = $1
      if (!(path in current))        print path, "MISSING", expected, ""
      else if (current[path] == expected) print path, "MATCH", expected, expected
      else                           print path, "MODIFIED", expected, current[path]
      seen[path] = 1
    }
    END { for (p in current) if (!(p in seen)) print p, "EXTRA", "", current[p] }
  ' "$work/current.tsv" "$work/signed.tsv" | LC_ALL=C sort
} > "$outdir/verify.csv"

LC_ALL=C awk -F'\t' '{ printf "%s  %s\n", $1, $2 }' "$work/current.tsv" > "$outdir/rebuilt.sha256"

manifest=$(wc -l < "$work/signed.tsv" | tr -d ' ')
LC_ALL=C awk -F',' -v manifest="$manifest" -v outdir="$outdir" '
NR == 1 { next }
$2 == "MATCH" { matched++ }
$2 == "MISSING" { missing++ }
$2 == "MODIFIED" { modified++ }
$2 == "EXTRA" { extra++ }
END {
  ok = (missing + modified + extra == 0) ? "true" : "false"
  f = outdir "/summary.json"
  printf "{\"manifest\":%d,\"match\":%d,\"missing\":%d,\"modified\":%d,\"extra\":%d,\"ok\":%s}\n", \
    manifest, matched, missing, modified, extra, ok > f
  close(f)
}' "$outdir/verify.csv"

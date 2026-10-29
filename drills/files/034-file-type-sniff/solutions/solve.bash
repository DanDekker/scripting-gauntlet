#!/usr/bin/env bash
# 034-file-type-sniff — trust the magic bytes, not the name.
set -euo pipefail

indir="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
[ -d "$indir" ] || { echo "no such directory: $indir" >&2; exit 1; }
mkdir -p "$outdir"

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
rows="$work/rows.csv"
: > "$rows"

for f in "$indir"/*; do
  [ -f "$f" ] || continue
  name=${f##*/}
  magic=$(head -c 8 "$f" | od -An -v -tx1 | tr -d ' \n')
  case "$magic" in
    1f8b*)     kind=gzip ;;
    89504e47*) kind=png ;;
    25504446*) kind=pdf ;;
    504b0304*) kind=zip ;;
    7f454c46*) kind=elf ;;
    ffd8ff*)   kind=jpeg ;;
    fffe*)     kind=utf16le ;;
    efbbbf*)   kind=utf8bom ;;
    *)
      if [ "$(LC_ALL=C tr -d '[:print:]\n\r\t' < "$f" | wc -c | tr -d ' ')" -eq 0 ]; then
        kind=ascii
      else
        kind=unknown
      fi
      ;;
  esac
  printf '%s,%s,%s\n' "$name" "$kind" "$magic" >> "$rows"
done

printf 'filename,kind,magic\n' > "$outdir/types.csv"
LC_ALL=C sort "$rows" >> "$outdir/types.csv"

LC_ALL=C awk -F',' -v outdir="$outdir" '
{
  files++
  kinds[$2] = 1
  if ($2 == "ascii" || $2 == "utf8bom" || $2 == "utf16le") text++
}
END {
  n = 0
  for (k in kinds) n++
  f = outdir "/summary.json"
  printf "{\"files\":%d,\"kinds\":%d,\"text_files\":%d}\n", files, n, text > f
  close(f)
}' "$rows"

#!/usr/bin/env bash
# 037-binary-inspect — walk the blob byte by byte.
set -euo pipefail

blob="${IN:?IN not set}/blob.bin"
outdir="${OUT:?OUT not set}"
[ -f "$blob" ] || { echo "no such file: $blob" >&2; exit 1; }
mkdir -p "$outdir"

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
od -An -v -tu1 "$blob" > "$work/bytes.txt"

LC_ALL=C awk -v outdir="$outdir" '
function matches(p, hex) { return substr(hexes, 2 * p - 1, length(hex)) == hex }
{ for (i = 1; i <= NF; i++) b[++n] = $i + 0 }
END {
  sname[1] = "png";  shex[1] = "89504e47"
  sname[2] = "gzip"; shex[2] = "1f8b"
  sname[3] = "pdf";  shex[3] = "25504446"
  sname[4] = "zip";  shex[4] = "504b0304"
  sname[5] = "elf";  shex[5] = "7f454c46"
  sname[6] = "jpeg"; shex[6] = "ffd8ff"

  for (p = 1; p <= n; p++) hexes = hexes sprintf("%02x", b[p])

  sf = outdir "/strings.txt"
  run = ""; start = 0
  for (p = 1; p <= n; p++) {
    v = b[p]
    if (v == 0) nuls++
    if (v >= 32 && v <= 126) {
      if (run == "") start = p - 1
      run = run sprintf("%c", v)
    } else {
      if (length(run) >= 4) { count++; printf "%d\t%s\n", start, run > sf }
      run = ""
    }
  }
  if (length(run) >= 4) { count++; printf "%d\t%s\n", start, run > sf }
  close(sf)

  magic = "none"; moff = -1; found = 0
  for (p = 1; p <= n && !found; p++)
    for (k = 1; k <= 6; k++)
      if (matches(p, shex[k])) { magic = sname[k]; moff = p - 1; found = 1; break }

  r = outdir "/report.json"
  printf "{\"size_bytes\":%d,\"nul_bytes\":%d,\"string_count\":%d,\"embedded_magic\":\"%s\",\"magic_offset\":%d}\n", n, nuls, count, magic, moff > r
  close(r)
}' "$work/bytes.txt"

#!/usr/bin/env bash
# 044-schema-drift — presence per header, type per column, then two sorts.
set -euo pipefail

indir="${IN:?IN not set}/daily"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

tmpd=$(mktemp -d)
trap 'rm -rf "$tmpd"' EXIT

LC_ALL=C awk -v tmpd="$tmpd" -v outdir="$outdir" '
BEGIN { FS = "," }
function trim(s) { gsub(/^[ \t\r]+|[ \t\r]+$/, "", s); return s }
function type_of(f, name,   key) {
  key = f SUBSEP name
  if (!(key in present)) return "absent"
  if ((nonempty[key] + 0) == 0) return "empty"
  if (!(key in notint)) return "int"
  if (!(key in notnum)) return "float"
  return "text"
}
FNR == 1 {
  fileno++
  fname = FILENAME
  sub(/.*\//, "", fname)
  files[fileno] = fname
  ncols = 0
  for (i = 1; i <= NF; i++) {
    name = trim($i)
    sub(/^\357\273\277/, "", name)
    if (name == "") continue
    idx[name] = i
    ncols++
    present[fname, name] = 1
    if (!(name in seen)) { seen[name] = 1; allnames[name] = 1; nall++ }
  }
  widths[fname] = ncols
  next
}
{
  if (trim($0) == "") next
  rows[fname]++
  for (name in idx) {
    v = trim($(idx[name]))
    if (v == "") continue
    key = fname SUBSEP name
    nonempty[key]++
    if (v !~ /^-?[0-9]+$/) notint[key] = 1
    if (v !~ /^-?[0-9]+(\.[0-9]+)?$/) notnum[key] = 1
  }
}
END {
  cols = tmpd "/columns.tsv"
  types = tmpd "/types.tsv"
  for (name in allnames) {
    first = ""; last = ""; cnt = 0
    for (i = 1; i <= fileno; i++) {
      f = files[i]
      if ((f, name) in present) {
        if (first == "") first = f
        last = f
        cnt++
      }
    }
    added = (first != files[1])
    dropped = (last != files[fileno])
    if (added && dropped) { status = "transient"; transient++ }
    else if (added)        { status = "added";     added_count++ }
    else if (dropped)      { status = "dropped";   dropped_count++ }
    else                   { status = "stable";    stable++ }
    printf "%s\t%s\t%s\t%d\t%s\n", name, first, last, cnt, status > cols

    line = name
    kinds = "/"; nkinds = 0
    for (i = 1; i <= fileno; i++) {
      cell = type_of(files[i], name)
      if (cell != "absent" && cell != "empty" && index(kinds, "/" cell "/") == 0) {
        kinds = kinds cell "/"
        nkinds++
      }
      line = line "\t" cell
    }
    drift = (nkinds > 1) ? "yes" : "no"
    if (nkinds > 1) drifted++
    print line "\t" drift > types
  }
  close(cols); close(types)

  total = 0
  for (i = 1; i <= fileno; i++) total += rows[files[i]] + 0
  dst = outdir "/files.csv"
  printf "file,rows,columns\n" > dst
  for (i = 1; i <= fileno; i++)
    printf "%s,%d,%d\n", files[i], rows[files[i]] + 0, widths[files[i]] > dst
  close(dst)

  dst = outdir "/summary.json"
  fmt = "{\"files\":%d,\"columns\":%d,\"rows\":%d,\"stable\":%d,\"added\":%d,\"dropped\":%d,\"transient\":%d,\"type_drift\":%d}\n"
  printf fmt, fileno, nall, total, stable, added_count, dropped_count, transient, drifted > dst
  close(dst)
}' "$indir"/*.csv

{
  printf 'column,first_seen,last_seen,files_present,status\n'
  LC_ALL=C sort -k2,2 -k1,1 "$tmpd/columns.tsv" | tr '\t' ','
} > "$outdir/columns.csv"

{
  printf 'column,2026-09-28,2026-09-29,2026-09-30,2026-10-01,drift\n'
  LC_ALL=C sort -k1,1 "$tmpd/types.tsv" | tr '\t' ','
} > "$outdir/types.csv"

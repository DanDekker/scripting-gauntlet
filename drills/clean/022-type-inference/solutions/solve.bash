#!/usr/bin/env bash
# 022-type-inference — two regexes for the type, five rules for the casualties.
set -euo pipefail

src="${IN:?IN not set}/columns.csv"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

awk -F',' -v outdir="$outdir" '
function isint(v) { return v ~ /^-?(0|[1-9][0-9]*)$/ }
function isfloat(v) { return v ~ /^-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?$/ }
function offends(v,   s) {
  if (v ~ /^-?0[0-9]+$/) return 1
  if (v ~ /^-?[0-9]+$/) {
    s = v; sub(/^-/, "", s)
    if (length(s) > 16) return 1
    if (length(s) == 16 && (s + 0) > 9007199254740991) return 1
    return 0
  }
  s = v; sub(/^[+-]/, "", s)
  if (tolower(s) == "nan" || tolower(s) == "infinity") return 1
  if (v ~ /^[+-]?0[xX][0-9a-fA-F]+$/) return 1
  return isfloat(v) ? 0 : 1
}
NR == 1 { ncol = NF; for (i = 1; i <= NF; i++) name[i] = $i; next }
{
  nrow++
  for (i = 1; i <= NF; i++) cell[i, nrow] = $i
}
END {
  types = outdir "/types.csv"
  offenders = outdir "/offenders.csv"
  print "column,type" > types
  print "column,row,value" > offenders
  for (i = 1; i <= ncol; i++) {
    allint = 1; allfloat = 1; decimal = 0
    for (r = 1; r <= nrow; r++) {
      v = cell[i, r]
      if (!isint(v)) allint = 0
      if (!isfloat(v)) allfloat = 0
      if (v ~ /[.eE]/) decimal = 1
    }
    if (allint) type = "integer"
    else if (allfloat && decimal) type = "float"
    else type = "string"
    line = name[i] "," type
    print line > types
    for (r = 1; r <= nrow; r++) {
      if (offends(cell[i, r])) {
        hit = name[i] "," cell[1, r] "," cell[i, r]
        print hit > offenders
      }
    }
  }
  close(types); close(offenders)
}' "$src"

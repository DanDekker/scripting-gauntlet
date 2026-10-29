#!/usr/bin/env bash
# 082-atomic-config - validate first, stage in the target directory, rename last.
set -euo pipefail

export LC_ALL=C
inp="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
target="$outdir/live/app.conf"
[[ -f "$target" ]] || { echo "missing $target" >&2; exit 1; }

first_bad() {
  awk '
    /^[[:space:]]*$/ || /^[[:space:]]*#/ { next }
    $0 !~ /^[a-z_][a-z0-9_]*=/ { print FNR; exit 1 }
  ' "$1"
}

mode_of() {
  if stat -c '%a' "$1" >/dev/null 2>&1; then stat -c '%a' "$1"; else stat -f '%Lp' "$1"; fi
}

applied=false
rejected=false
for name in update.valid update.invalid; do
  file="$inp/$name"
  [[ -r "$file" ]] || { echo "cannot read $file" >&2; exit 1; }
  if line=$(first_bad "$file"); then
    mode=$(mode_of "$target")
    tmp="$outdir/live/.app.conf.$$.tmp"
    cat "$file" > "$tmp"
    chmod "$mode" "$tmp"
    mv "$tmp" "$target"
    applied=true
  else
    printf 'rejected %s:%s\n' "$name" "$line" >> "$outdir/reject.log"
    rejected=true
  fi
done

mode=$(mode_of "$target")
printf '{"applied":%s,"rejected":%s,"mode":"%s"}\n' \
  "$applied" "$rejected" "$mode" > "$outdir/summary.json"

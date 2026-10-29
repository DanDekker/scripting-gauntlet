#!/usr/bin/env bash
# Audit a PEM bundle with the openssl CLI.
#
# `openssl x509 -noout -text` is used rather than `-ext subjectAltName`: macOS still
# ships LibreSSL 3.3, which has no `-ext` flag. The human-readable dump is the
# portable subset every OpenSSL/LibreSSL build agrees on.
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

epoch_from_openssl() {
  date -u -j -f "%b %d %H:%M:%S %Y GMT" "$1" +%s 2>/dev/null || date -u -d "$1" +%s
}
epoch_from_iso() {
  date -u -j -f "%Y-%m-%dT%H:%M:%SZ" "$1" +%s 2>/dev/null || date -u -d "$1" +%s
}
iso_from_epoch() {
  date -u -r "$1" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d "@$1" +%Y-%m-%dT%H:%M:%SZ
}

audit_raw=$(tr -d '[:space:]' < "$in_dir/audit_time.txt")
audit_epoch=$(epoch_from_iso "$audit_raw")
deadline_epoch=$((audit_epoch + 30 * 86400))

# Split the concatenated bundle into one file per certificate.
awk -v dir="$work" '
  /-----BEGIN CERTIFICATE-----/ { n++; file = sprintf("%s/cert%03d.pem", dir, n) }
  { if (file != "") print > file }
' "$in_dir/bundle.pem"

: > "$work/certs.tsv"
: > "$work/names.tsv"
for cert in "$work"/cert*.pem; do
  [ -s "$cert" ] || continue
  text=$(openssl x509 -in "$cert" -noout -text) || {
    echo "cannot read certificate $cert" >&2
    exit 1
  }
  cn=$(printf '%s\n' "$text" | awk '
    /^[[:space:]]*Subject:/ {
      line = $0
      sub(/^[[:space:]]*Subject:[[:space:]]*/, "", line)
      n = split(line, parts, /,[[:space:]]*/)
      for (i = 1; i <= n; i++) {
        if (parts[i] ~ /^CN[[:space:]]*=/) {
          v = parts[i]
          sub(/^CN[[:space:]]*=[[:space:]]*/, "", v)
          print v
          exit
        }
      }
    }')
  raw_after=$(printf '%s\n' "$text" \
    | sed -n 's/^[[:space:]]*Not After[[:space:]]*:[[:space:]]*//p' | head -1)
  if [ -z "$cn" ] || [ -z "$raw_after" ]; then
    echo "certificate $cert has no CN or no expiry" >&2
    exit 1
  fi
  after_epoch=$(epoch_from_openssl "$raw_after")
  if [ "$after_epoch" -le "$audit_epoch" ]; then
    status=expired
  elif [ "$after_epoch" -le "$deadline_epoch" ]; then
    status=warning
  else
    status=ok
  fi
  not_after=$(iso_from_epoch "$after_epoch")
  printf '%s\t%s\t%s\n' "$cn" "$not_after" "$status" >> "$work/certs.tsv"

  printf '%s\n' "$text" | grep -o 'DNS:[^,[:space:]]*' | sed 's/^DNS://' | while IFS= read -r name; do
    printf '%s\t%s\n' "$status" "$name" >> "$work/names.tsv"
  done
  # The common name is a name the certificate also answers to.
  printf '%s\t%s\n' "$status" "$cn" >> "$work/names.tsv"
done

{
  printf 'cn,not_after,status\n'
  sort -t"$(printf '\t')" -k2,2 -k1,1 "$work/certs.tsv" \
    | awk -F'\t' '{ printf "%s,%s,%s\n", $1, $2, $3 }'
} > "$out_dir/certs.csv"

total=$(wc -l < "$work/certs.tsv" | tr -d ' ')
expired=$(awk -F'\t' '$3=="expired"' "$work/certs.tsv" | wc -l | tr -d ' ')
warning=$(awk -F'\t' '$3=="warning"' "$work/certs.tsv" | wc -l | tr -d ' ')
ok=$(awk -F'\t' '$3=="ok"' "$work/certs.tsv" | wc -l | tr -d ' ')

# A target is covered by any cert that is not expired.
covers() {
  local target pattern
  target=$(printf '%s' "$1" | tr 'A-Z' 'a-z')
  while IFS="$(printf '\t')" read -r status name; do
    [ "$status" = "expired" ] && continue
    pattern=$(printf '%s' "$name" | tr 'A-Z' 'a-z')
    if [ "$pattern" = "$target" ]; then
      return 0
    fi
    case "$pattern" in
      '*.'*)
        suffix=".${pattern#\*.}"
        case "$target" in
          *"$suffix")
            head=${target%"$suffix"}
            if [ -n "$head" ]; then
              case "$head" in
                *.*) ;;
                *) return 0 ;;
              esac
            fi
            ;;
        esac
        ;;
    esac
  done < "$work/names.tsv"
  return 1
}

{
  printf '{\n'
  printf '  "audit_time": "%s",\n' "$audit_raw"
  printf '  "total_certs": %s,\n' "$total"
  printf '  "expired_count": %s,\n' "$expired"
  printf '  "warning_count": %s,\n' "$warning"
  printf '  "ok_count": %s,\n' "$ok"
  printf '  "uncovered_targets": ['
  first=1
  while IFS= read -r target; do
    target=$(printf '%s' "$target" | tr -d '[:space:]')
    [ -n "$target" ] || continue
    if ! covers "$target"; then
      [ "$first" -eq 1 ] || printf ',\n'
      first=0
      printf '    "%s"' "$target"
    fi
  done < "$in_dir/targets.txt"
  [ "$first" -eq 1 ] || printf '\n  '
  printf ']\n}\n'
} > "$out_dir/coverage.json"

#!/usr/bin/env bash
# Decode JWT claims with base64 + jq and judge every token against the pinned "now".
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

now=$(tr -d '[:space:]' < "$in_dir/now.txt")
now_epoch=$(printf '%s' "$now" | jq -R 'fromdateiso8601')

# base64url -> JSON text. A part that already ends in '=' is already a multiple of 4.
b64d() {
  local s=$1
  s=${s//-/+}
  s=${s//_/\/}
  case $(( ${#s} % 4 )) in
    1) return 1 ;;
    2) s="${s}==" ;;
    3) s="${s}=" ;;
  esac
  printf '%s' "$s" | base64 -d 2>/dev/null
}

trim() {
  local s=$1
  s="${s#"${s%%[![:space:]]*}"}"
  s="${s%"${s##*[![:space:]]}"}"
  printf '%s' "$s"
}

: > "$scratch/rows"
: > "$scratch/subs"

index=0
malformed=0
none_alg=0
expired=0
not_yet_valid=0
valid_count=0

while IFS= read -r raw || [ -n "$raw" ]; do
  line=$(trim "${raw%$'\r'}")
  [ -z "$line" ] && continue
  index=$((index + 1))

  dots=${line//[^.]/}
  [ "${#dots}" -ne 2 ] && continue

  head=${line%%.*}
  rest=${line#*.}
  payload_part=${rest%%.*}

  ok=1
  header=$(b64d "$head") || ok=0
  payload=$(b64d "$payload_part") || ok=0
  if [ "$ok" -eq 1 ]; then
    jq -e 'type == "object"' <<<"$header" >/dev/null 2>&1 || ok=0
    jq -e 'type == "object"' <<<"$payload" >/dev/null 2>&1 || ok=0
  fi

  if [ "$ok" -eq 0 ]; then
    malformed=$((malformed + 1))
    printf '%s,malformed,,\n' "$index" >> "$scratch/rows"
    continue
  fi

  record=$(jq -rn --argjson h "$header" --argjson p "$payload" --argjson now "$now_epoch" '
    def ic($o; $k):
      if (($o[$k]? | type) == "number") and (($o[$k]) == (($o[$k]) | floor))
      then $o[$k] else null end;
    (ic($p; "exp")) as $exp
    | (ic($p; "nbf")) as $nbf
    | (if ($h.alg? == "none") then "none-alg"
       elif ($exp != null and $exp <= $now) then "expired"
       elif ($nbf != null and $nbf > $now) then "not-yet-valid"
       else "valid" end) as $status
    | (if (($p.sub? | type) == "string") then $p.sub else "" end) as $sub
    | [$status, $sub, (if $exp == null then "" else ($exp | tostring) end)]
    | join("\u001f")
  ')

  IFS=$'\x1f' read -r status subject exp_value <<<"$record"
  exp_value=${exp_value:-}
  subject=${subject:-}

  case "$status" in
    none-alg) none_alg=$((none_alg + 1)) ;;
    expired) expired=$((expired + 1)) ;;
    not-yet-valid) not_yet_valid=$((not_yet_valid + 1)) ;;
    valid) valid_count=$((valid_count + 1)) ;;
  esac
  [ -n "$subject" ] && printf '%s\n' "$subject" >> "$scratch/subs"
  printf '%s,%s,%s,%s\n' "$index" "$status" "$subject" "$exp_value" >> "$scratch/rows"
done < "$in_dir/tokens.txt"

tokens=$(wc -l < "$scratch/rows" | tr -d ' ')
subjects=0
if [ -s "$scratch/subs" ]; then
  subjects=$(sort -u "$scratch/subs" | wc -l | tr -d ' ')
fi

{
  printf 'index,status,sub,exp\n'
  cat "$scratch/rows"
} > "$out_dir/tokens.csv"

jq -n \
  --argjson tokens "$tokens" \
  --argjson malformed "$malformed" \
  --argjson none_alg "$none_alg" \
  --argjson expired "$expired" \
  --argjson not_yet_valid "$not_yet_valid" \
  --argjson valid "$valid_count" \
  --argjson subjects "$subjects" \
  '{tokens: $tokens,
    malformed: $malformed,
    none_alg: $none_alg,
    expired: $expired,
    not_yet_valid: $not_yet_valid,
    valid: $valid,
    subjects: $subjects}' > "$out_dir/summary.json"

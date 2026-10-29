#!/usr/bin/env bash
# Redact secrets, emails and card numbers with jq's regex engine (Oniguruma).
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

src="$in_dir/output.txt"
[ -f "$src" ] || { printf 'missing %s\n' "$src" >&2; exit 1; }

keys='api_key|apikey|secret|password|passwd|token|authorization|access_key'

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

# One pass over the whole file: keep the line count, remember whether the last byte was
# a newline, then redact each line in rule order.
jq -R -s --arg keys "$keys" '
  def secretpat:
    "(?i)(?<key>" + $keys + ")(?<sep>[ \t]*[=:][ \t]*)(?<val>.*?)"
    + "(?=(?:[ \t]+(?:" + $keys + ")[ \t]*[=:]|$))";
  def emailpat: "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z0-9.-]+";
  def cardpat: "(?<![0-9])[0-9](?:[ -]?[0-9]){12,18}(?![ -]?[0-9])";
  def rstrip: sub("[ \t]+$"; "");
  def placeheld:
    . as $v
    | ((["redacted", "****", "xxxxx", "null", "none"] | index($v | ascii_downcase)) != null);
  def sensitive: . as $v | (($v | length) >= 6) and (($v | placeheld) | not);
  def capstr($n): (([.captures[] | select(.name == $n)][0].string) // "");

  . as $all
  | ($all | endswith("\n")) as $nl
  | (if $all == "" then []
     else ($all | split("\n") | if $nl then .[:-1] else . end) end) as $lines
  | ($lines | map(
      . as $orig
      | ([match(secretpat; "g")]
         | map(select((capstr("val") | rstrip) as $v | ($v | sensitive)))
         | length) as $nsec
      | (gsub(secretpat;
          "\(.key)\(.sep)\(if (.val | rstrip | sensitive) then "[REDACTED]" else .val end)")) as $s1
      | ([$s1 | match(emailpat; "g")] | length) as $nmail
      | ($s1 | gsub(emailpat; "[EMAIL]")) as $s2
      | ([$s2 | match(cardpat; "g")] | length) as $ncard
      | ($s2 | gsub(cardpat; "[CARD]")) as $s3
      | {line: $s3, secrets: $nsec, emails: $nmail, cards: $ncard, changed: ($s3 != $orig)}
    )) as $rows
  | {text: (($rows | map(.line) | join("\n")) + (if $nl then "\n" else "" end)),
     summary: {lines: ($rows | length),
               secrets: ($rows | map(.secrets) | add // 0),
               emails: ($rows | map(.emails) | add // 0),
               cards: ($rows | map(.cards) | add // 0),
               changed: ($rows | map(if .changed then 1 else 0 end) | add // 0)}}
' "$src" > "$scratch/agg.json"

jq -j '.text' "$scratch/agg.json" > "$out_dir/redacted.txt"
jq '.summary' "$scratch/agg.json" > "$out_dir/summary.json"

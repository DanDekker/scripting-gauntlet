#!/usr/bin/env bash
# Rebuild a chat completion from a captured SSE stream.
# Events end at blank lines; data fields join with newlines; [DONE] is a sentinel.
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

msg_raw="$scratch/message.bin"
chunks="$scratch/chunks.tsv"
: > "$msg_raw"
: > "$chunks"

# One pass to drop the CR of a CRLF capture and any trailing whitespace.
sed -e 's/[[:space:]]*$//' "$in_dir/stream.txt" > "$scratch/lines.txt"

# Four output lines per block: kind, a, b, c.
#   C -> a=delta_len, b=role (base64), c=content (base64)
#   U -> a=prompt_tokens, b=completion_tokens, c=''
JQ_EVENT='
  ( if (.choices | type) == "array" and ((.choices | length) > 0) then
      ((.choices[0].delta // {}) as $d
       | "C",
         ((($d.content) | if type == "string" then length else 0 end) | tostring),
         ((($d.role) | if type == "string" then @base64 else "" end)),
         ((($d.content) | if type == "string" then @base64 else "" end)))
    else empty end ),
  ( if (.usage | type) == "object" then
      ("U", ((.usage.prompt_tokens // 0) | tostring), ((.usage.completion_tokens // 0) | tostring), "")
    else empty end )
'

total_events=0
comment_lines=0
valid_chunks=0
malformed_chunks=0
completed=0
prompt_tokens=0
completion_tokens=0
comments=0
pending=0
data_lines=()

flush() {
  if [ "$pending" -eq 0 ]; then
    comments=0
    data_lines=()
    return 0
  fi
  total_events=$((total_events + 1))
  comment_lines=$((comment_lines + comments))

  if [ "${#data_lines[@]}" -gt 0 ]; then
    payload=$(printf '%s\n' "${data_lines[@]}")
    if [ -z "$payload" ]; then
      malformed_chunks=$((malformed_chunks + 1))
    elif [ "$payload" = "[DONE]" ]; then
      completed=1
    elif blocks=$(printf '%s\n' "$payload" | jq -r "$JQ_EVENT" 2>/dev/null); then
      while IFS= read -r kind; do
        IFS= read -r fa || fa=""
        IFS= read -r fb || fb=""
        IFS= read -r fc || fc=""
        case "$kind" in
          C)
            valid_chunks=$((valid_chunks + 1))
            role=$(printf '%s' "$fb" | base64 -d 2>/dev/null || true)
            printf '%s\t%s\t%s\n' "$valid_chunks" "$fa" "$role" >> "$chunks"
            if [ -n "$fc" ]; then
              printf '%s' "$fc" | base64 -d >> "$msg_raw"
            fi
            ;;
          U)
            prompt_tokens=${fa:-0}
            completion_tokens=${fb:-0}
            ;;
        esac
      done <<< "$blocks"
    else
      malformed_chunks=$((malformed_chunks + 1))
    fi
  fi

  comments=0
  data_lines=()
  pending=0
}

while IFS= read -r line || [ -n "$line" ]; do
  if [ -z "$line" ]; then
    flush
    continue
  fi
  pending=1
  case "$line" in
    :*) comments=$((comments + 1)) ;;
    data:*)
      value=${line#data:}
      value=${value# }
      data_lines+=("$value")
      ;;
  esac
done < "$scratch/lines.txt"
flush

{
  printf 'chunk_index,delta_len,role\n'
  if [ -s "$chunks" ]; then
    awk -F'\t' '{ printf "%s,%s,%s\n", $1, $2, $3 }' "$chunks"
  fi
} > "$out_dir/chunks.csv"

if [ -s "$msg_raw" ]; then
  cp "$msg_raw" "$out_dir/message.txt"
  printf '\n' >> "$out_dir/message.txt"
else
  : > "$out_dir/message.txt"
fi

total_chars=$(jq -R -s 'length' "$msg_raw")

jq -n \
  --argjson total_events "$total_events" \
  --argjson comment_lines "$comment_lines" \
  --argjson valid_chunks "$valid_chunks" \
  --argjson malformed_chunks "$malformed_chunks" \
  --argjson total_chars "$total_chars" \
  --argjson completed "$completed" \
  --argjson prompt_tokens "$prompt_tokens" \
  --argjson completion_tokens "$completion_tokens" \
  '{total_events: $total_events, comment_lines: $comment_lines,
    valid_chunks: $valid_chunks, malformed_chunks: $malformed_chunks,
    total_chars: $total_chars, completed_done: ($completed == 1),
    prompt_tokens: $prompt_tokens, completion_tokens: $completion_tokens}' \
  > "$out_dir/summary.json"

#!/usr/bin/env bash
set -euo pipefail

list="$IN/tests.txt"
if command -v python3 >/dev/null; then py=(python3)
elif command -v python >/dev/null; then py=(python)
elif command -v py >/dev/null; then py=(py -3)
else echo "need Python 3" >&2; exit 1
fi
[[ -r "$list" && -r "$IN/test_case.py" ]] || { echo "missing test list or runner" >&2; exit 1; }
printf 'test,exit_code,stdout,stderr\n' > "$OUT/results.csv"
tests=0
passed=0
failed=0
mkdir -p "$WORK/ran"
while IFS= read -r name || [[ -n "$name" ]]; do
  [[ -z "$name" || "$name" == \#* ]] && continue
  [[ "$name" =~ ^[a-z-]+$ ]] || { echo "bad test name: $name" >&2; exit 1; }
  tests=$((tests + 1))
  if "${py[@]}" "$IN/test_case.py" "$name" > "$WORK/stdout" 2> "$WORK/stderr"; then
    code=0; passed=$((passed + 1))
  else
    code=$?; failed=$((failed + 1))
  fi
  stdout=$(tr '\n' ' ' < "$WORK/stdout")
  stderr=$(tr '\n' ' ' < "$WORK/stderr")
  printf '%s,%d,%s,%s\n' "$name" "$code" "$stdout" "$stderr" >> "$OUT/results.csv"
  printf '%d\n' "$code" > "$WORK/ran/$name"
done < "$list"
printf '{"tests":%d,"passed":%d,"failed":%d}\n' "$tests" "$passed" "$failed" > "$OUT/summary.json"
if [[ "$failed" -gt 0 ]]; then echo "$failed test(s) failed" >&2; exit 1; fi

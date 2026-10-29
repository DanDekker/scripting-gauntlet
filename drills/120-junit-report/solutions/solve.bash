#!/usr/bin/env bash
# Flatten a JUnit XML report with awk: only the <testcase> elements are truth.
set -euo pipefail

src="${IN:?IN not set}/report.xml"
out_dir="${OUT:?OUT not set}"
mkdir -p "$out_dir"
[[ -f $src ]] || { echo "missing $src" >&2; exit 1; }

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

awk '
function unescape(s) {
  gsub(/&lt;/, "<", s)
  gsub(/&gt;/, ">", s)
  gsub(/&quot;/, "\"", s)
  gsub(/&apos;/, sprintf("%c", 39), s)
  gsub(/&amp;/, "\\&", s)
  return s
}

function attr(tag, name,   pat, at, rest, j) {
  pat = " " name "=\""
  at = index(tag, pat)
  if (at == 0) return ""
  rest = substr(tag, at + length(pat))
  j = index(rest, "\"")
  if (j == 0) return ""
  return unescape(substr(rest, 1, j - 1))
}

function scan(fragment) {
  if (index(fragment, "<failure") > 0) has_failure = 1
  if (index(fragment, "<error") > 0) has_error = 1
  if (index(fragment, "<skipped") > 0) has_skipped = 1
}

function emit(   state) {
  state = "pass"
  if (has_error) state = "error"
  else if (has_failure) state = "fail"
  else if (has_skipped) state = "skip"
  printf "%s\t%s\t%s\t%s\t%.3f\n", case_suite, case_class, case_name, state, case_time + 0
}

function open_case(line,   at, rest, j, tag, tail) {
  at = index(line, "<testcase")
  rest = substr(line, at)
  j = index(rest, ">")
  tag = (j > 0) ? substr(rest, 1, j) : rest
  case_suite = suite
  case_class = attr(tag, "classname")
  case_name = attr(tag, "name")
  case_time = attr(tag, "time")
  has_failure = 0; has_error = 0; has_skipped = 0
  tail = (j > 0) ? substr(rest, j + 1) : ""
  scan(tag)
  scan(tail)
  if (substr(tag, length(tag) - 1) == "/>") { emit(); in_case = 0 }
  else if (index(tail, "</testcase>") > 0) { emit(); in_case = 0 }
  else in_case = 1
}

BEGIN { suite = ""; in_case = 0; case_time = "0" }

{
  line = $0
  if (in_case) {
    scan(line)
    if (index(line, "</testcase>") > 0) { emit(); in_case = 0 }
    next
  }
  if (index(line, "</testsuite>") > 0) { suite = ""; next }
  if (match(line, /<testsuite[ >]/)) {
    tag = substr(line, index(line, "<testsuite"))
    cut = index(tag, ">")
    if (cut > 0) tag = substr(tag, 1, cut)
    suite = attr(tag, "name")
    next
  }
  if (index(line, "<testcase") > 0) { open_case(line); next }
}
' "$src" > "$scratch/rows.tsv"

{
  printf 'suite,class,name,status,time\n'
  awk -F'\t' '
    function q(s) {
      if (index(s, ",") || index(s, "\"")) {
        gsub(/"/, "\"\"", s)
        return "\"" s "\""
      }
      return s
    }
    { printf "%s,%s,%s,%s,%s\n", q($1), q($2), q($3), $4, $5 }
  ' "$scratch/rows.tsv"
} > "$out_dir/tests.csv"

awk -F'\t' '
  function jsonq(s) { gsub(/\\/, "\\\\", s); gsub(/"/, "\\\"", s); return "\"" s "\"" }
  {
    tests++
    if ($4 == "pass") passed++
    else if ($4 == "fail") failed++
    else if ($4 == "error") errored++
    else if ($4 == "skip") skipped++
    total += $5 + 0
    if (tests == 1 || $5 + 0 > best) { best = $5 + 0; slowest = $3 }
  }
  END {
    printf "{\"tests\":%d,\"passed\":%d,\"failed\":%d,\"errored\":%d,\"skipped\":%d,\"time\":%.3f,\"slowest\":%s}\n", tests, passed, failed, errored, skipped, total, jsonq(slowest)
  }
' "$scratch/rows.tsv" > "$out_dir/summary.json"

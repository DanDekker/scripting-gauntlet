---
name: text-munging
description: Extract, count, bucket, and summarize logs, dumps, configs, and other unstructured text with awk, grep, sed, perl-style regex, or lua patterns. Use when asked what is in a log file, to find the top N of anything, to bucket events by time, to normalize or filter lines, or to extract fields from output that was never designed for you. Not for parsing structured formats that already have a parser.
license: MIT
metadata:
  family: text-munging
  drill: 002-log-triage
---

# Text munging

Logs, command output, dumps. The shape is always: **one line at a time, one regex per
line, tab-separated out.**

## The workhorses

```bash
# top-N anything
sort access.log | uniq -c | sort -rn | head -20

# extract with a capture group (one field per line)
sed -nE 's/.*"([A-Z]+) ([^ ]+) HTTP.*/\1\t\2/p' access.log

# count by extracted field
awk -F'"' 'NF>2 { split($3, s, " "); c[s[1]]++ } END { for (k in c) print c[k], k }' access.log
```

## Splitting the awkward field

Combined-log and syslog lines put the interesting part between quotes or brackets. Do not
write a monster regex — **split on the delimiter that already separates the noise**:

```awk
# "GET /x HTTP/1.1" 200 — split on the quote first, then on spaces
n = split($0, q, "\""); split(q[2], r, " "); split(q[3], s, " ")
method = r[1]; path = r[2]; status = s[1]
```

Quoted fields with spaces inside (`"Mozilla/5.0 (Macintosh; Intel Mac OS X)"`) are exactly
why field-splitting beats `$4`-style positional access.

## Traps

- **Lines that almost match.** If your regex requires a trailing space it will skip the
  last field. Anchor on what is always there, then validate the capture (`/^\d{3}$/`).
- **Multi-line records.** Stack traces and pretty-printed JSON are not line-oriented.
  Either pre-join continuations or parse the whole file.
- **Silent drops.** Count unparsed lines and report them. A pipeline that quietly loses
  3% of records produces a confident wrong answer.
- **Query strings.** `/api/users?page=2` is five distinct paths until you strip `?.*`.
- **ANSI colour.** Strip `\e\[[0-9;]*m` before matching, or your regex fails on prod output.
- **Locale sorting.** `sort` differs across environments; set `LC_ALL=C` when byte order
  matters to the answer.

## Bucketing time

Parse to epoch, integer-divide, format back — never regex the timestamp display form twice.

```bash
# per-hour counts from ISO timestamps
awk '{ h = substr($0, index($0,"T")+1, 2); c[h]++ } END { for (k in c) print k, c[k] }'
```

## Reporting

Top-N plus a total plus a skipped count. "12 records, 1 unparseable, 7×200" is the answer
to "what did the traffic look like". Prove it against `drills/002-log-triage`.

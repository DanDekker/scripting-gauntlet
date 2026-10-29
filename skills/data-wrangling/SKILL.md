---
name: data-wrangling
description: Filter, dedupe, join, aggregate, and reshape messy tabular or JSON data using awk, jq, python, or lua. Use when asked to summarize, clean, compare, count, or convert a CSV, TSV, JSON, or JSONL export; when a spreadsheet is too big or too dirty to open; or when someone needs a number out of a data dump in minutes. Not for building ETL pipelines or warehouses.
license: MIT
metadata:
  family: data-wrangling
  drill: 001-csv-rollup
---

# Data wrangling

You have messy rows and someone wants a number. The job is `read → transform → write`,
and it is done when the number is right.

## Pick the tool by shape, not habit

| data | first choice | why |
| --- | --- | --- |
| CSV/TSV, no quoted commas | `awk -F,` | one pass, no dependencies, fits in a one-liner |
| CSV with quoting/newlines in fields | python `csv` | hand-rolled splitting will corrupt rows |
| JSON, already on disk | `jq` | it *is* the tool for this |
| JSONL, huge | python (streaming) or `jq -c` | don't load 4 GB into memory |
| needs a join against another file | python dicts, or `sort` + `join` | awk associative arrays work too |
| needs floats and money | python | awk is float-native but formatting bites |

Reaching for pandas for a 200-row export is the classic overreach: 40 lines, a dependency,
and slower than `awk`.

## The four moves

**1. Filter.** One predicate, applied per line.

```bash
awk -F, 'NR>1 && $5 > 1000' orders.csv
jq -c 'select(.status == "paid")' events.jsonl
```

**2. Dedupe.** Group by key, pick the winner, say which rule you used.

```awk
# keep the row with the latest timestamp per id (ISO timestamps sort as strings)
{ if (!(id=$1 in ts) || $6 > ts[$1]) { ts[$1]=$6; row[$1]=$0 } }
END { for (k in row) print row[k] }
```

Always state the tie-break (latest? first? longest?) — an unstated rule is a bug report
waiting to happen.

**3. Aggregate.** Bucket, count, sum.

```awk
{ sum[$3] += $5; cnt[$3]++ }
END { for (k in sum) printf "%s,%d,%.2f\n", k, cnt[k], sum[k] }
```

**4. Reshape.** CSV↔JSON→records→TSV. Write the six lines; don't install a converter.

```bash
jq -r '.[] | [.id, .name] | @csv' data.json
```

## Traps that actually bite

- **Money as text.** `$1,200.00` needs `[$,]` stripped before parsing. Blank is *not* zero
  — count it separately.
- **Mixed case keys.** `NORTH`, `north`, `North ` are three groups until you trim and fold.
- **Sorting numbers as strings.** `10` sorts before `9`. Use numeric sort or cast.
- **`sort | uniq -c` order.** Alphabetical by key, not by count. Pipe through
  `sort -rn` and remember the count lands in field 1.
- **Two-field sort.** "Revenue desc, name asc" is `sort -k2,2nr -k1,1`, not one `sort`.
- **Header row.** `NR>1` assumes line 1 is the header; verify it before trusting it.
- **CRLF and BOM.** A trailing `\r` breaks your regex and your last field.

## Reporting

Print the count of what you *dropped* alongside what you kept. "7 orders, 1 dropped for a
blank amount" is a trustworthy answer; "3675.75" alone is not.

See [references/awk-recipes.md](references/awk-recipes.md) for portable one-liners.
Prove it against `drills/001-csv-rollup`.

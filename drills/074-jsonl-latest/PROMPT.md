# 074-jsonl-latest

> "The event stream is append-only but full of retries. For each id I want the newest
> record, and I need to know how many rows that removed."

## Task

`in/events.jsonl` is one JSON object per line:
`{"id": <str>, "ts": <ISO-8601 UTC "YYYY-MM-DDTHH:MM:SSZ">, "status": <str>}`.

## Rules

1. Blank lines, including whitespace-only lines, are skipped.
2. Every other line must be a JSON object with string `id`, `ts` and `status`, or the run
   fails with the line number on stderr.
3. Timestamps are all UTC in the same fixed-width format, so plain string order is time order.
4. Keep the record with the greatest `ts` per `id`; on an exact tie the **later line** wins.
5. Ids are unique in the output, sorted ascending in byte order (`LC_ALL=C`).

## Output

- `out/latest.csv` - header `id,ts,status`, one row per id, ascending by id.
- `out/summary.json` - exactly three integers: `records` (non-blank records read), `ids`
  (rows written), `dropped` (records replaced by a newer row).

## Messes to expect

- a blank line between records, and a record with leading spaces
- ids arriving out of order
- two records with the same timestamp, where the later line is newer
- an older record for an id that already appeared

## Timebox

3 minutes. One pass in input order, `if ts >= best[id]` overwrites.

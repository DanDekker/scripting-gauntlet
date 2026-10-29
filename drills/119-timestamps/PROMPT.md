# 119-timestamps

> "Six services write to one log and each one stamps its lines differently. I cannot sort
> it, so I cannot see what happened first. Normalise every line to one format and put them
> in order."

## Input

`in/entries.log` — one entry per line, each beginning with a timestamp in one of these
shapes:

| shape | example |
|---|---|
| ISO-8601 UTC | `2026-10-29T12:00:00Z` |
| ISO-8601 with offset | `2026-10-29T14:00:00+02:00` |
| naive, dash date | `2026-10-29 12:00:00` |
| naive, slash date | `2026/10/29 12:00:00` |
| UNIX epoch seconds | `1767225600` |
| syslog | `Oct 29 12:00:00 2026` |

`in/tz.txt` holds the fixed zone name for the naive formats: the literal string `UTC`.
Naive timestamps in this drill are therefore UTC — never local time.

## Rules

1. **Blank lines are not entries.** A line of spaces or tabs is skipped and does not count
   in `lines`.
2. **A timestamp is a token followed by whitespace.** Try the formats in this order, each
   anchored at the very start of the line, and the character right after the timestamp must
   be a space or a tab. If it is not, that shape does not match and nothing else is tried
   for a date-shaped line: `2026-10-29T12:00:00Zno-space-after` has no timestamp and is
   skipped.
   1. ISO-8601: `YYYY-MM-DDTHH:MM:SS`, optional `.fff` fractional seconds (dropped, the
      second is unchanged), then either `Z` or a numeric offset `+HH:MM` / `-HH:MM`.
   2. `YYYY-MM-DD HH:MM:SS` — naive, UTC.
   3. `YYYY/MM/DD HH:MM:SS` — naive, UTC.
   4. A bare integer, possibly negative — UNIX epoch seconds.
   5. `Mon DD HH:MM:SS YYYY` — syslog, naive, UTC. The month name is case-insensitive and
      the day may be space-padded (`Oct  9 12:00:00 2026`, two spaces).
3. **Invalid timestamps are skipped**, not guessed at: a `Z` followed by a numeric offset
   (`2026-10-29T12:00:00Z+02:00`) fails rule 2's trailing-whitespace test; and a timestamp
   whose fields are out of range (month 1–12, day 1–31, hour 0–23, minute 0–59,
   second 0–59) is skipped. An offset means the instant is the wall clock minus the
   offset: `14:00:00+02:00` is `12:00:00Z`.
4. **Output format.** Always ISO-8601 UTC with a `Z` and no fractional part:
   `YYYY-MM-DDTHH:MM:SSZ`. Epoch `0` is `1970-01-01T00:00:00Z`; negative epochs are
   before it.
5. **Order.** Sort by the normalised timestamp (i.e. by the instant) ascending. Entries on
   the same second keep their original input order.
6. **The message** is what is left after the timestamp token and the single whitespace
   character that follows it, with trailing whitespace stripped. Leading spaces beyond that
   one are kept.

## Output

Write exactly these files to `$OUT`:

1. **`out/entries.csv`** — header `timestamp,message`. One row per accepted entry, sorted as
   above. Quote a `message` with `"` when it contains a comma or a double quote, doubling
   any inner quote; otherwise write it bare. `timestamp` never needs quoting.
2. **`out/summary.json`** — an object with exactly these keys:
   - `lines` — non-blank input lines (int)
   - `parsed` — accepted entries, i.e. rows in `entries.csv` (int)
   - `skipped` — non-blank lines with no usable timestamp (int), so
     `parsed + skipped == lines`
   - `first` — the normalised timestamp of the first row in sorted order, or `""` when
     nothing parsed
   - `last` — the normalised timestamp of the last row in sorted order, or `""`

   Print it as one compact JSON object: `{"lines":17,"parsed":13,...}`.

## Messes to expect

- `2026-10-29T14:00:00+02:00` is `12:00:00Z`, so it ties with `2026-10-29T12:00:00Z`, the
  syslog noon line and the `.123Z` line — five entries share that second and stay in input
  order; `2026-10-29T10:00:00Z` is a second of its own, one hour earlier
- `2026-10-29T12:00:00.123Z` keeps the second `12:00:00`, the fraction is dropped
- `oct 29 12:00:05 2026` (lowercase month) and `Oct  9 12:00:00 2026` (padded day) both
  parse; the second one is eleven days earlier
- `0` and `-1000000000` are valid epochs, not junk
- `2026-10-29T12:00:00Z+02:00`, `2026-10-29T12:00:00Zno-space-after`, `no timestamp here
  at all` and `2026-13-45 99:99:99` are the four skipped lines
- the last line has trailing spaces after its message; they are stripped
- the message `with comma, in the message` must come out quoted

## Timebox

Four minutes. If you are past that, the approach is wrong.

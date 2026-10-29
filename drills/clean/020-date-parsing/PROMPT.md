# 020-date-parsing

> "Five systems exported dates five different ways and I need one sortable column."

## Task

`in/dates.csv` has `id,raw` — one human-or-machine date per row.

## Rules

1. Recognise exactly these six shapes, after trimming surrounding whitespace:
   - `YYYY-MM-DD`
   - `MM/DD/YYYY` — **month first, always** (US ordering), so `01/02/2026` is January 2
   - `YYYYMMDD`
   - `D Month YYYY`, e.g. `5 March 2026`
   - `Mon D YYYY`, e.g. `Mar 5 2026`
   - an ISO timestamp `YYYY-MM-DDThh:mm:ss` with a `Z` or `±hh:mm` offset
2. For a timestamp take the **calendar date as written**; never shift it into UTC.
3. A shape that is well-formed but impossible (`31/02/2026`, month `13`) is **invalid**,
   exactly like a value that matches no shape at all.
4. Invalid rows get an empty `date`, are counted in `failed`, and are excluded from
   `earliest`/`latest`.
5. Output dates are `YYYY-MM-DD`; rows keep the input order.

## Output

**`out/normalised.csv`** — header `id,date`, one row per input row.

**`out/summary.json`** — exactly five keys: `rows`, `parsed`, `failed`, `earliest`,
`latest` (ISO strings).

## Messes to expect

- the same day written four ways in four rows
- `01/02/2026`, which is January 2 under the month-first rule
- a timestamp carrying a negative offset
- `31/02/2026`, `2026-13-01`, and `not-a-date`

## Timebox

3 minutes. One month-name table and one days-in-month check. Do not shell out to `date`.

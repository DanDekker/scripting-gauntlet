# 185-ps1-datetime

> "Two feeds, two date formats. The European one keeps landing on the wrong day because
> the parser guesses American."

## Input

`in/stamps.csv` — header `id,stamp`. Each stamp is one of two shapes:

- `YYYY-MM-DDTHH:MM:SSZ` — a UTC instant
- `DD/MM/YYYY` — a **European** calendar date, meaning midnight UTC

## Rules

1. Parse with explicit patterns. The day-first shape must be read as day **first**.
2. An impossible date (`31/02/2026`) is **invalid**: counted and excluded.
3. Convert each accepted stamp to Unix seconds assuming UTC. Reject a stamp that matches
   neither shape.
4. Sort rows by `id` ascending numerically.

## Output

Write exactly these files to `$OUT`:

1. **`out/epochs.csv`** — header `id,epoch`, one row per accepted stamp.
2. **`out/summary.json`** — keys `rows`, `invalid`, `earliest` (the smallest epoch).
   One compact JSON object: `{"rows":4,"invalid":1,"earliest":0}`.

## Messes to expect

- `03/04/2026` is 3 April, not March 4
- `31/02/2026` does not exist: invalid, not rolled into March
- `1970-01-01T00:00:00Z` is epoch `0`, which is falsy in a lot of code
- a DateTime parsed without a kind is neither local nor UTC until you say so

## Timebox

Five minutes. `[datetime]::ParseExact` with `dd/MM/yyyy`, and `[datetime]::SpecifyKind(...,'Utc')`
before `ToUnixTimeSeconds`.

# 102-secret-scan

> "Scan this repo tree before I push it. I know there will be noise — what I want is the
> lines that are actually keys, with the file and line so I can go rotate them."

## Input

`in/tree/` — a directory tree of text files (several subdirectories, `.example` samples,
files with no credentials at all).

## Rules

A **candidate** is a line containing a key name — case-insensitively — from this list:
`api_key`, `apikey`, `secret`, `password`, `passwd`, `token`. The key name must be
followed by `=` or `:` (optionally with spaces), then a value: quoted (`"…"`, `'…'`) or
unquoted.

- The key name is found anywhere on the line, so `DB_PASSWORD = x` and `API_KEY: x` are
  both candidates.
- A sentence that merely says `the api_key rotation` is **not** a candidate: the key name
  is not followed by `=` or `:`. Neither is `The token endpoint lives at /oauth/token.`
- **One line is at most one candidate and at most one finding**: the *first* key name on
  the line wins.

Given a candidate, its **value** is the text after the `=`/`:` and any spaces:

- if it starts with a quote, the value is everything up to the matching quote
  (so `"correct horse battery staple"` is one value, and trailing spaces after the
  closing quote are ignored);
- otherwise the value is everything up to the first space or tab.

The value is a **secret** only if all of these hold:

1. the file is *not* a sample file — a path ending in `.example` or `.example.txt` is a
   sample file: its candidates are still counted in `candidates`, but they are never
   secrets (`in/tree/deploy/prod.env.example` is the deliberate case);
2. the value is not empty;
3. the value, compared case-insensitively, is not one of the placeholders `CHANGEME`,
   `changeme`, `your-key-here`, `xxx`, `TODO`, `example`, `<redacted>`;
4. the value is **8 characters or longer** (7 characters is not a secret, 8 is).

The **key** recorded for a finding is the matched key name exactly as written in the
source, with its original case: `SERVICE_TOKEN="x"` records `TOKEN`, `DB_PASSWORD = 'x'`
records `PASSWORD`, `Api_Key = "x"` records `Api_Key`.

## Output

Write exactly these files to `$OUT`:

1. **`out/findings.csv`** — header `file,line,key,value`. One row per secret, sorted by
   `file` ascending (the path **relative to `in/tree/`**, `/`-separated), then `line`
   ascending (numeric). `line` is 1-based. `value` is the secret with quotes stripped — it
   **is** printed: the point of the scan is to route it to a human. The same value in two
   files is two rows.
2. **`out/summary.json`** — an object with exactly these keys:
   - `files_scanned` — files under the tree (int)
   - `candidates` — every candidate line, including placeholders and sample-file hits (int)
   - `secrets` — rows in `findings.csv` (int)
   - `unique_values` — distinct secret values (int)
   - `sample_files` — files under the tree whose path ends in `.example` or `.example.txt`
     (int)

## Messes to expect

- `deploy/notes.txt` has a quoted value with spaces *and* trailing spaces after the quote,
  an `apikey:` with no value at all, and `token=abc1234` — 7 characters, so not a secret
- `deploy/prod.env.example` looks like the worst file in the tree (three keys) and leaks
  nothing: sample files are candidates only
- `app/legacy.ini` has two key names on one line after a bad merge: only the first is
  reported
- `scripts/setup.sh` has a real key in a comment and a `<redacted>` placeholder two lines
  below it
- `app/config.py` and `app/client.py` share one secret value: two findings, one unique value
- `scripts/clean.md` has none: no candidates, no findings

## Timebox

A few minutes. If you are past that, the approach is wrong.

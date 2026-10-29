# 108-redact-output

> "This log dump is going into the transcript and it has credentials in it. Strip them —
> but leave the placeholders we already wrote alone, and don't tell me a card number or an
> inbox address is harmless just because there is no `password =` in front of it."

## Input

`in/output.txt` — captured tool output, one line per line.

The file is messy in realistic ways: a secret on the very first line, a secret on the last
line with **no trailing newline**, a value split across two lines, values that are already
placeholders (`api_key = REDACTED`, `password = ****`), an empty value, a value of two
characters, a value of five characters, an email address in mixed case, a 16-digit card
number written with spaces and another with hyphens, a 12-digit run and a 20-digit run
(neither is card-like), a long hex string that is **not** after a key name, the same secret
twice, a line with two different secrets, and trailing whitespace on a line that gets
redacted.

## Rules

1. **A secret is a key/value pair.** The key is one of `api_key`, `apikey`, `secret`,
   `password`, `passwd`, `token`, `authorization`, `access_key`, compared
   **case-insensitively**, and it must be a whole word: nothing precedes it, or what
   precedes it is not a letter, digit or `_`. The key must be followed by `=` or `:`.
2. **Keep what you did not leak.** The key text and the `=`/`:` separator — including any
   spaces around them — are preserved exactly as written.
3. **The value runs to the end of the line**, with two refinements:
   - spaces immediately after the separator belong to the separator, not the value;
   - if another key (same list, same whole-word rule) followed by `=`/`:` starts later on
     the line, the value stops just before the spaces that precede that key.
   Trailing whitespace at the end of a line is not part of the value.
4. **Is the value sensitive?** A value is sensitive unless it is empty, or is one of the
   placeholders `REDACTED`, `redacted`, `****`, `xxxxx`, `null`, `none` (compared
   case-insensitively), or is shorter than 6 characters. Quotes are ordinary characters:
   `token = ""` has a 2-character value, and `api_key = "REDACTED"` has a 10-character
   value that is *not* the placeholder `REDACTED`.
5. **Redact it.** A sensitive value is replaced with the literal string `[REDACTED]`.
   Everything from the first character of the value to the end of the line goes with it, so
   trailing whitespace on a redacted line disappears.
6. **Emails.** An email address anywhere on the line (inside a value or not) is replaced
   with `[EMAIL]`. An email is a run of `A-Z a-z 0-9 . _ % + -`, then `@`, then a run of
   `A-Z a-z 0-9 . -` that contains at least one dot.
7. **Card numbers.** A card-like run is 13 to 19 digits in which a single space or a single
   hyphen may sit between any two neighbouring digits. The whole run — separators included
   — is replaced with `[CARD]`. A run of 12 or fewer digits, or of 20 or more digits, is
   not card-like and is left alone; a 20-digit run must not be truncated into a card.
8. **Order matters.** Apply rule 5 to the line first, then rule 6 to the result, then
   rule 7 to *that* result. A line whose value is not sensitive is untouched by rule 5 but
   can still be hit by rules 6 and 7.
9. Every other line is copied through unchanged.

## Output

Write exactly these files to `$OUT`:

1. **`out/redacted.txt`** — the redacted text, one output line per input line, in input
   order, nothing added or dropped. A trailing newline is present **iff** the input had one
   (this fixture's input does not).
2. **`out/summary.json`** — an object with exactly these keys:
   - `lines` — number of lines (int)
   - `secrets` — number of secret values redacted by rule 5 (int)
   - `emails` — number of email addresses replaced by rule 6 (int)
   - `cards` — number of card-like runs replaced by rule 7 (int)
   - `changed` — number of lines whose final text differs from the original line (int)

## Messes to expect

- `api_key = REDACTED`, `password = ****` and `token = xxxxx` are already placeholders and
  must survive untouched; `secret = abc12` is 5 characters and survives too.
- `password: hunter2@example.com` is redacted **as a secret**: rule 5 runs first, so the
  address is gone before rule 6 sees it and `emails` does not count it.
- `user=bob token: tok_9a8b7c6d5e password=hunter2hunter2` is two secrets on one line, so
  `token`'s value stops before `password` rather than swallowing it.
- `api_key = sk-live-9f8a` / `7b6c5d4e3f2a1b` is one secret split across two lines: the
  second half has no key in front of it, so it stays. That is the honest failure mode of
  line-oriented redaction — do not invent a rule to catch it.
- `4111 1111 1111 1111` and `5500-0000-0000-0004` are cards; `123456789012` (12 digits)
  and `12345678901234567890` (20 digits) are not.
- the 40-character hex string after `commit` is not a secret and not a card.

## Timebox

Four minutes. If you are past that, the approach is wrong.

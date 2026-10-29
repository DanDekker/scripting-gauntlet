# 112-jwt-claims

> "Support keeps asking whether a token is still good. I've got a pile of them, a
> timestamp for 'now', and no willingness to stand up a verifier. Decode them, read the
> claims, and tell me per token: still good, already dead, or suspicious."

## Input

- `in/tokens.txt` — one token per line, `header.payload.signature`, where each part is
  base64url **without** padding. Blank lines are allowed.
- `in/now.txt` — one ISO-8601 UTC timestamp, e.g. `2026-10-29T12:00:00Z`. That timestamp
  is "now" for every token; nothing reads the real clock.

The file is messy in realistic ways: a line with only two parts, a payload that is not
valid JSON, a header that decodes to a JSON array instead of an object, a token whose
signature part is empty (`h.p.`), an `alg` of `none`, an `alg` of `None`, an `exp` in the
past, an `nbf` in the future, a token that is both expired and not-yet-valid, a token with
no `exp`, an `exp` that is the string `"tomorrow"`, a part that already carries `=`
padding, a `sub` that is a number, a token with an unknown extra claim (`scope`, `iss`),
and a line with trailing spaces.

## Rules

1. **Lines.** Trim leading and trailing whitespace from a line before looking at it (a
   trailing space after the signature is noise). Blank lines are skipped. A line that does
   not have **exactly three** `.`-separated parts is not a JWT and is skipped entirely — it
   produces no row and is counted nowhere, but it still occupies an index.
2. **Index.** `index` is the 1-based position of the line among all **non-blank** input
   lines (blank lines do not consume an index). A skipped two-part line does consume one.
3. **Decoding.** For part 0 (header) and part 1 (payload): translate `-` to `+` and `_` to
   `/`, pad with `=` to a multiple of 4, decode, and parse as JSON. The signature part is
   never decoded. A token is **malformed** when a part fails to decode or does not parse to
   a JSON **object** (an array, a string, a number, or broken JSON all count). A malformed
   token is not inspected further: no `alg`, no claims, no subject.
4. **Claims.** `exp` and `nbf` are integer numbers of seconds since the UNIX epoch. A claim
   that is absent, or present but not an integer number (a string, `true`, a float, an
   object), is **ignored** for that check. A token with no usable `exp` never expires.
5. **Status**, first match wins:
   - `malformed` — rule 3.
   - `none-alg` — the header's `alg` is exactly `none` (**case-sensitive**; `None` is not
     `none`). Checked before expiry, so an expired `alg=none` token is `none-alg`.
   - `expired` — `exp` is usable and `exp <= now`.
   - `not-yet-valid` — `nbf` is usable and `nbf > now`. (A token that is both expired and
     not-yet-valid is `expired`.)
   - `valid` — otherwise.
6. **Subject.** The `sub` claim when it is present and a string; otherwise the empty
   string. A numeric `sub` is not a subject.

## Output

Write exactly these files to `$OUT`:

1. **`out/tokens.csv`** — header `index,status,sub,exp`.
   - One row per line that had exactly three parts, in **input order**.
   - `index` — rule 2 (int).
   - `status` — exactly one of `malformed`, `none-alg`, `expired`, `not-yet-valid`, `valid`.
   - `sub` — the subject, or empty.
   - `exp` — the `exp` value as a plain integer, or empty when there is no usable integer
     `exp` (including on malformed tokens).
   - Values contain no commas, so no quoting is needed.
2. **`out/summary.json`** — an object with exactly these keys:
   - `tokens` — lines that had exactly three parts (int)
   - `malformed`, `none_alg`, `expired`, `not_yet_valid`, `valid` — counts of each status (int);
     the five add up to `tokens`
   - `subjects` — distinct non-empty subjects among **decoded** tokens (int); a malformed
     token contributes no subject, and the same subject on two tokens counts once

## Messes to expect

- the two-part line is index 2: it produces no row but still consumes an index, and the
  blank line above it consumes none
- the header that decodes to `[]` is `malformed` even though its payload is fine
- the `alg` of `None` is *not* `none-alg` — it is an ordinary token and its `exp` decides
- `"exp": "tomorrow"` is ignored, so that token is `valid` with an empty `exp`
- the token with both a past `exp` and a future `nbf` is `expired`, not `not-yet-valid`
- a part that already ends in `=` must not get a second pad added
- `h.p.` (empty signature) is a three-part line and is judged normally

## Timebox

Four minutes. If you are past that, the approach is wrong.

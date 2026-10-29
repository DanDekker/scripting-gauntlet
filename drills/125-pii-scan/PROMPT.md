# 125-pii-scan

> "Before we ship these support tickets to a model, tell me what personal data is in them —
> and I mean the real thing. Last week's scanner flagged every order id in the file because
> a 16-digit number looked like a card."

## Input

`in/tickets.txt` — one ticket per line. A ticket may be long and carry several fields, so a
line can hold more than one piece of personal data.

The file is messy on purpose: an email in the middle of a sentence, phone numbers written
with spaces, dashes and dots (and one with `+1 (…)`), a 16-digit number that fails its
checksum, a 16-digit number that passes, a 15-digit card number, an SSN-shaped value with
area `000`, one with area `666`, a public IPv4 next to a private one, a `172.x` address
inside the private range and one outside it, a 9-digit order id, a 22-digit reference, two
emails whose local part ends in a phone number (one starting at the same column as the phone,
one starting earlier), blank lines, a whitespace-only line and trailing spaces.

## Rules

Each detected value is one **finding**. Values are found independently and every kind is
scanned over the whole line, then overlapping matches are resolved.

1. **`email`** — the pattern `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}`.
2. **`card`** — a run of digits joined by single spaces or single dashes whose **digit count**
   is 13 to 19 and whose **Luhn checksum** is valid (double every second digit counting from
   the right, subtract 9 from anything over 9, the total is a multiple of 10). 12 digits is
   not a card, 20 digits is not a card, and 16 digits that fail Luhn is not a card.
3. **`ssn`** — `[0-9]{3}-[0-9]{2}-[0-9]{4}` whose area (the first three digits) is not `000`,
   not `666`, and not in `900`-`999`. The match must not be glued to another digit on either
   side.
4. **`private-ip`** — a dotted quad of four 1-3 digit octets, none over 255, whose first
   octet is `10`, or is `192` with second octet `168`, or is `172` with a second octet in
   `16`-`31`. The match must not be glued to another digit or a dot on either side. A public
   address is not PII for this drill.
5. **`phone`** — exactly **10 digits** in the number, optionally written with single spaces,
   dashes or dots between digits, optionally prefixed by `+` and a 1-3 digit country code,
   optionally with a parenthesised area code: `+1 (555) 010-2030`, `(555) 010-2030`,
   `555-010-2030`, `555.010.2030`, `555 010 2030`. A number with **no** separators and no `+`
   is **not** a phone (so a bare 10-digit run is an order id), and a 9-digit run is never a
   phone. The match must not be glued to another digit on either side.
6. **Resolve overlaps.** A line is read left to right: the find with the **earlier start**
   wins. When two finds start at the same column, the **longer** one wins. A rejected find
   never appears, and its columns are consumed by the one that beat it.

## Output

Write exactly these files to `$OUT`:

1. **`out/findings.csv`** — header `ticket,line,kind,value`.
   - `ticket` is the 1-based number of the ticket line in the input; blank lines do not count
     as tickets.
   - `line` is the same number: the input is one ticket per line, so the two columns coincide
     (they exist so the shape matches a file scanner).
   - `kind` is one of `email`, `card`, `ssn`, `private-ip`, `phone`.
   - `value` is the matched text **exactly as it appears in the input**, separators included
     (`555-010-2030`, not `5550102030`). No value contains a comma, so fields are written
     raw.
   - Sorted by `ticket` ascending, then by the column where the match starts ascending (1 is
     the first character of the line), then `kind` ascending.
2. **`out/summary.json`** — an object with exactly these keys:
   - `tickets` — non-blank input lines (int)
   - `findings` — rows written (int)
   - `by_kind` — object mapping each kind **present in the output** to its count; a kind with
     no findings does not appear
   - `tickets_flagged` — tickets with at least one finding (int)
   - `unique_values` — distinct matched values across all findings (int)

## Messes to expect

- `4111 1111 1111 1111` is a card; `4111 1111 1111 1112` is not (Luhn) — the ticket that only
  carries the second one has **no** findings
- `3782 822463 10005` is a card with 15 digits
- `123-45-6789` is an SSN; `000-12-3456` and `666-12-3456` are not
- `10.2.3.4`, `192.168.1.20` and `172.20.5.9` are private; `8.8.8.8` and `172.40.5.9` are not
  PII and must not be reported
- `123456789` (9 digits) and `1234567890123456789012` (22 digits) are numbers, not cards or
  phones
- `+1 (555) 010-2030` is one phone value, written with its separators
- in `support-555-010-2031@example.com` the email starts before the phone, so only the email
  is reported; in `555-010-2032@example.net` both start at the same column and the longer
  match (the email) wins
- blank lines and the whitespace-only line are not tickets: `tickets` counts the 11 real ones

## Timebox

Five minutes. One scan per kind, one sort, one pass to resolve overlaps. Validation is the
whole point: a shape without a check is a false positive.

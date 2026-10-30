# 212-perl-local-global

> "The wide records came out separated by commas, and then every record after the first
> wide one was separated by semicolons too. The formatter had one separator setting in a
> package global: it set a `my` copy inside the helper (which the helper never reads)
> and assigned the global directly on another path (which never came back)."

## Input

`in/records.txt` — one record per line, `<kind> <value>`:

```text
# kind value
plain alpha
wide bravo
plain charlie
wide delta
plain epsilon
```

## Rules

1. Read `in/records.txt`. Skip blank lines and lines starting with `#`. Each remaining
   line is a kind and a value, separated by a single space.
2. The program has **one separator setting**, a package global that starts as `,`.
   A helper routine renders a record by joining its kind and value with whatever the
   separator currently is. The helper reads the same global the rest of the program
   uses — there is only one setting.
3. A record of kind `wide` is rendered with `;` as the separator. Every other record is
   rendered with `,`.
4. The separator setting must be back to `,` when the program finishes. A wide record
   must not change the separator for the records that follow it.
5. **`out/report.txt`** — the rendered records, one per line, in input order.
   - `plain alpha` -> `plain,alpha`
   - `wide bravo` -> `wide;bravo`
6. **`out/summary.json`** — keys `records`, `wide`, `sep_after`. One compact JSON object.
   - `records` — the number of records.
   - `wide` — the number of `wide` records.
   - `sep_after` — the separator setting once the program has finished. It is the text
     `,` (a comma), not a description of it.

## Messes to expect

- `my $SEP = ";"` inside a sub creates a **new lexical variable**. The helper routine
  reads the package global, so the override never reaches it — the wide record is
  rendered with a comma.
- Assigning to the package global directly (`$SEP = ";"`) does reach the helper, but it
  never comes back: every later record is rendered with a semicolon.
- `local $SEP = ";"` changes the global for the enclosing block and restores the old
  value when that block ends.

## Timebox

Five minutes.

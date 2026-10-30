# 205-perl-foreach-alias

> "The mailing-list tool started printing capitalized names in the 'original names'
> column. The normalizer ran `foreach (@names) { $_ = ucfirst $_; }` — and `foreach`
> hands you aliases, not copies, so the source list was rewritten underneath the report."

## Input

`in/names.txt` — one name per line:

```text
ada lovelace
  grace hopper
ALAN TURING
jean-luc picard
```

## Rules

1. Read `in/names.txt` into a list, one entry per line. Strip only the line
   separator; keep everything else, including any leading spaces.
2. **Normalize** a name: trim leading and trailing whitespace, then uppercase the
   first character and leave the rest of the name exactly as it was.
   - `ada lovelace` -> `Ada lovelace`
   - `  grace hopper` -> `Grace hopper`
   - `ALAN TURING` -> `ALAN TURING` (the first character is already uppercase)
3. **`out/normalized.csv`** — header `index,name`. One row per name, in file order,
   `index` starting at 1, `name` the normalized form.
4. **`out/original.csv`** — header `index,name`. The same list **as it stands after
   step 3** — it must still hold the names exactly as they were read from the file.
   The caller needs the untouched list for a second report.
5. **`out/summary.json`** — keys `names`, `changed`. One compact JSON object.
   - `names` — the number of names.
   - `changed` — the number of names whose normalized form differs from the original.

## Messes to expect

- `foreach` aliases the elements of the list it walks. `foreach my $n (@names) { $n = ... }`
  rewrites `@names` itself. `map` and `grep` alias `$_` the same way.
- To change the list without changing the source, work on a copy.

## Timebox

Five minutes. `my @work = @names;` gives you a list you are free to modify.

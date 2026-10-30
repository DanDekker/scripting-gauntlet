# 215-perl-utf8-bytes

> "The mailing-list normalizer reported `café` as 5 characters long and uppercased it to
> `café` with the accent untouched. Perl strings are byte strings: the file was read as
> bytes, so `length` counted bytes and `uc` only uppercased the ASCII letters."

## Input

`in/names.txt` — one display name per line, UTF-8:

```text
ada
café
Jörg
zoë
marguerite
```

## Rules

1. Read `in/names.txt` as UTF-8 text, one name per line. Skip blank lines.
2. For each name, report:
   - the **uppercased** name — every character is uppercased, so `café` becomes `CAFÉ`
     and `Jörg` becomes `JÖRG`;
   - `chars` — the number of **characters** in the name as written. `café` is 4
     characters, even though it is 5 bytes.
3. **`out/names.csv`** — header `index,name,chars`. One row per name, in file order,
   `index` starting at 1.
4. **`out/summary.json`** — keys `names`, `chars`, `longest`. One compact JSON object.
   - `names` — the number of names.
   - `chars` — the total number of characters across all the names.
   - `longest` — the character count of the longest name.

## Messes to expect

- A perl string is a **byte string** until it is decoded. Read the file without an
  encoding layer and `length` counts bytes: `café` is 5, not 4.
- `uc` on undecoded bytes only uppercases the ASCII letters, so the accent survives and
  the name is not really uppercased.
- Decode on the way in (an `:encoding(UTF-8)` layer, or `Encode::decode`) and encode on
  the way out.

## Timebox

Five minutes.

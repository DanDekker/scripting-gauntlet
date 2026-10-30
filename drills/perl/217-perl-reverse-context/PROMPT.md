# 217-perl-reverse-context

> "The tail of the log viewer came back as one long line: `eerht eelcrahc owt ovrahb eno
> ahpla`. The reversal was assigned to a scalar, so `reverse` reversed the *joined text*
> instead of the list of records."

## Input

`in/records.txt` — one record per line:

```text
alpha one
bravo two
charlie three
```

## Rules

1. Read `in/records.txt`, one record per line, in file order. Skip blank lines.
2. Produce the records in **reverse order**: the last record comes first, the first
   record comes last. The records themselves are unchanged — the order is reversed, not
   the characters inside each record.
3. **`out/records.csv`** — header `index,record`. One row per record, in the reversed
   order, `index` starting at 1.
4. **`out/summary.json`** — keys `records`, `first`, `last`. One compact JSON object.
   - `records` — the number of records.
   - `first` — the first record of the reversed order (the last record of the file).
   - `last` — the last record of the reversed order (the first record of the file).

## Messes to expect

- `reverse` is **context sensitive**. In list context it reverses the list. In scalar
  context it joins the elements into one string and reverses the characters.
- `my $reversed = reverse @records;` gives you the mangled text; `my @reversed =
  reverse @records;` gives you the reversed list.

## Timebox

Four minutes.

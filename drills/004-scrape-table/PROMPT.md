# 004-scrape-table

> "Vendor page is down half the time so I saved the HTML. Grab the plan table out of it
> so I can diff it against last quarter."

## Task

`in/pricing.html` is a saved page. Extract the pricing table.

## Rules

1. Parse **only** the table with `id="pricing"`. The page also contains a hidden
   mobile duplicate (`class="mobile-only"`) with different prices — it must not appear
   in your output. Ignoring it is the point of the drill.
2. Inside a cell, `collapse whitespace` to single spaces and trim. Decode HTML entities
   (`&amp;` → `&`).
3. Ignore text inside `<span class="badge">` — the badge is decoration, not part of the
   plan name.
4. **Price**: strip `$` and thousands separators, then parse as a number.

## Output

**`out/pricing.csv`** — header, then one row per plan:

```
plan,seats,monthly_usd
Enterprise,500,2499.00
```

Ordered by `monthly_usd` **descending**, ties broken by `plan` **ascending**. Price is
formatted to exactly 2 decimal places.

## Messes to expect

- a nested `<span>` inside one plan name
- an entity (`&amp;`) in a plan name
- a cell whose text sits on its own line, padded with newlines
- a thousands separator in the most expensive price
- a second, hidden table with the same plan names and different prices

## Timebox

5 minutes. `html.parser` in python, or a scoped pattern match in lua. `awk`/`sed` on
HTML is the wrong instinct here — this is exactly the point where markup stops being a
text format and becomes a tree.

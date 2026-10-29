# 128-listing-scrape

> "The parts page throttles me, so I saved it. Turn the listing into a CSV I can load —
> names, prices, links — and tell me what the page left broken."

## Task

`in/page.html` is a saved product listing. Extract one row per sellable item.

## Rules

1. **An item** is a `<div>` element whose `class` attribute contains the token `item`.
   The class attribute is a space-separated list and the token must match exactly:
   `class="item featured"` is an item, `class="itemized promo"` is not, and a `<div>`
   with no class is not. An element belongs to the innermost item `<div>` that encloses
   it. A nested item `<div>` inside an item is **also** an item in its own right, and
   the outer item keeps the elements that sit directly in it (all of them, before and
   after the nested block). Elements that are not inside any item `<div>` are decoration
   and are ignored.
2. Inside an item, the **name** is the text of its `<span class="name">`, the **price**
   is the text of its `<span class="price">`, and the **link** is the `href` attribute of
   its `<a class="link">`. `class` must be exactly `name` / `price` / `link`. When an
   item carries more than one candidate element for a field, the **first one in document
   order** wins.
3. **Text extraction**: take the raw inner text, decode the entities
   `&amp; &lt; &gt; &quot; &#39; &apos;` (`&amp;` last, so `&amp;lt;` stays `&lt;`), then
   collapse every run of whitespace — spaces, tabs and newlines — to a single space and
   trim the result.
4. **A price is valid** only when its trimmed text matches `^\$[0-9,]+(\.[0-9]{1,2})?$`.
   Drop the `$` and the commas and write the amount with exactly 2 decimals (`$7` →
   `7.00`, `$1,299.00` → `1299.00`). A price element whose text is not a valid price —
   or an item with no price element at all — means the item has **no price** (empty
   column), never `0.00`.
5. An item with no name element, or whose name is empty after normalisation, is
   **skipped** and counted in `skipped`.
6. An item with no `<a class="link">`, or whose `<a class="link">` has no `href`,
   has an **empty link**. A relative href is kept exactly as written (do not resolve
   it); an absolute href is kept exactly as written. The href is trimmed.
7. **Deduplicate** on the pair `(name, price)`. When two items share both, the **first**
   one in document order is kept and the later one is counted in `duplicates`.

## Output

Write exactly these files to `$OUT`:

**`out/items.csv`** — header `name,price,link`, then one row per kept item, in document
order of first occurrence. `price` is the 2-decimal string or empty; `link` is the href or
empty. Fields are quoted only when they contain a comma or a double quote (then `"` is
doubled), RFC 4180 style.

```
name,price,link
Widget & Co,12.50,/p/1
```

**`out/summary.json`** — an object with exactly these keys:

| key | meaning |
|---|---|
| `items` | every item block found, including the skipped and the duplicate ones |
| `kept` | rows in `items.csv` |
| `skipped` | item blocks with no usable name |
| `duplicates` | item blocks dropped by rule 7 |
| `priced` | kept items with a non-empty price |
| `unpriced` | kept items with an empty price |
| `total` | sum of the kept prices, a JSON number with exactly 2 decimals, `0.00` when none |

`items = kept + skipped + duplicates` and `kept = priced + unpriced` must both hold.

## Messes to expect

- an item with **no** `<span class="price">` at all, and one whose price text is
  `Out of stock` — both are unpriced
- `$1,299.00` (thousands separator), `$7` (no decimals), `$2.5` (one decimal)
- names with `&amp;` `&lt;` `&gt;` `&quot;` `&#39;` `&apos;`; one name spans two lines
  with padding whitespace, another is padded with spaces and one with tabs
- a duplicated item (same name, same price) further down the page
- an item with no name element, and one whose name is only whitespace
- `<a class="link">` with no `href`, one with a relative href, one with an absolute
  `https://` href, one with padded whitespace around the href
- a `<div class="itemized promo">` block that looks like a product but is **not** an item
- one item `<div>` nested inside another
- trailing whitespace on element text, and one trailing-whitespace line in the markup

## Timebox

4 minutes. `html.parser` in python; in bash, split the markup on `<`/`>` so each tag is
its own line and walk it with `awk`, keeping a stack for `<div>` nesting.

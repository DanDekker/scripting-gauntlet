# 011-xml-attrs

> "Vendor sends XML. Attributes hold the ids, child elements hold the rest."

## Task

`in/catalog.xml` is a small XML document. Extract one row per `<product>`.

## Rules

1. `id` and `price` are **attributes** of `<product>`. `name` is a child element.
2. `<tag>` may repeat inside a product. Collect them in document order and join with `|`.
3. A product with no `<tag>` gets an **empty** tags cell — not the text `none`.
4. Sort rows by `id` **ascending**.

## Output

**`out/products.csv`** — header, then one row per product:

```
id,name,price,tags
A-1,Bolt,0.50,steel|small
```

**`out/summary.json`** — exactly one key: `products` (the number of rows).

## Messes to expect

- an XML declaration on the first line
- a product with no `<tag>` children
- repeated `<tag>` elements

## Timebox

4 minutes. `xml.etree` in python; in the shell, scope a regex to one element at a time
rather than trying to parse the whole document in one pass.

# 010-json-flatten

> "Catalog API returns nested blobs. I need one row per product for the spreadsheet."

## Task

`in/catalog.json` holds a document with a `products` array. Each product has a nested
`specs` object and a nested `tags` array.

## Rules

1. One output row per product, flattened:
   - `sku` — `product.sku`
   - `name` — `product.name`
   - `price` — `product.price` (a number)
   - `material` — `product.specs.material`
   - `weight` — `product.specs.weight` (a number)
   - `tags` — the tags joined by `|`, in the order they appear
2. Sort rows by `sku` **ascending**.
3. `generated` is a document-level field — it belongs in the summary, not in the rows.

## Output

**`out/flat.csv`** — header, then one row per product:

```
sku,name,price,material,weight,tags
A-1,Bolt,0.5,steel,12,steel|small
```

**`out/meta.json`** — exactly two keys: `generated` (the document's `generated` value) and
`count` (how many products).

## Messes to expect

- a product whose tags array has two entries
- a specs object nested two levels down from the array element
- products that are not in sku order in the source

## Timebox

3 minutes. `jq` with a path expression, or `product["specs"]["material"]` in python.

# 195-ps1-pipeline-unrolling

> "A batch processing helper extracts items from log lines. Whenever a batch contained exactly
> one item, PowerShell's pipeline automatically unrolled the array into a raw scalar, causing
> downstream type assertions (`-is [array]`) to fail."

## Input

`in/batches.txt` — colon-delimited `<id>:<items>` where items are comma-separated:

```
101:alpha,beta,gamma
102:solo
103:
104:one,two
105:isolated
```

Blank lines and `#` comments are skipped.

## Rules

Implement a function `Get-BatchItems($raw)`:
1. Parse the comma-delimited item list after the colon.
2. Return an array:
   - If empty string: empty array `@()`
   - If one item: single-element array `@($item)`
   - If multiple items: array of items
3. **Prevent pipeline unrolling**: return the array using the unary comma operator (`return ,$arr`) or `Write-Output -NoEnumerate $arr` so that the returned object remains a true array (`-is [array]`) even when it contains 0 or 1 elements.
4. For each batch, record:
   - `id`: integer batch ID
   - `count`: number of items
   - `is_array`: `"true"` if the received object `-is [array]`, else `"false"`
   - `first`: first item, or empty string `""` if empty

## Output

Write exactly these files to `$OUT`:

1. **`out/batches.csv`** — header `id,count,is_array,first`.
2. **`out/summary.json`** — keys `batches`, `total_items`, `single_item_batches`, `empty_batches`.
   One compact JSON object:
   `{"batches":5,"total_items":7,"single_item_batches":2,"empty_batches":1}`.

## Messes to expect

- Returning `@('solo')` without a comma causes PowerShell to output `[string]'solo'`, so `$res -is [array]` is false.
- Returning `@()` without a comma yields `$null`.

## Timebox

Four minutes. Use `return ,$items` to preserve array envelope.

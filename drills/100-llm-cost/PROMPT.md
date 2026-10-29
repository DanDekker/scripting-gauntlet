# 100-llm-cost

> "Here is last month's request log and the pricing sheet finance gave me. What did we
> spend, per model and in total — and which requests could you not price at all?"

## Input

`in/usage.jsonl` — one JSON object per request:

```json
{"request_id": "r1", "model": "small", "input_tokens": 1200, "output_tokens": 300, "cached": false}
```

- `request_id` (string) — the request identifier; **not** unique
- `model` (string) — matched against the pricing table exactly, case-sensitively
- `input_tokens` (number)
- `output_tokens` (number) — optional
- `cached` (boolean) — optional, defaults to `false`

`in/pricing.csv` — header `model,input_per_1k,output_per_1k`. `input_per_1k` is the price
per **1000 input tokens**, `output_per_1k` the price per **1000 output tokens**. Both are
decimal numbers (`0.015`).

## Rules

1. **Junk is skipped, not counted.** Drop blank lines, lines that are not valid JSON,
   lines that are JSON but not an object, and objects missing any of `request_id`,
   `model`, `input_tokens`. Every other object is a request, in input order.
2. **Not deduped.** A `request_id` that appears twice is two requests. Both are costed
   and both get a row.
3. **Cost of one request:**

   ```
   cost = input_tokens / 1000 * input_rate + output_tokens / 1000 * output_rate
   ```

   `output_tokens` is 0 when absent. When `cached` is `true`, the input half is charged at
   `input_rate * 0.1` (the cache rate — 10% of the normal input rate); the output half is
   unaffected.
4. **Rounding.** Each request's cost is rounded to 6 decimal places. The summary total is
   the sum of those **rounded** per-request costs, itself rounded to 6 decimals. `by_model`
   totals are the same rounded per-request costs summed per model.
5. **Unpriced.** A request whose `model` is not a row in `pricing.csv` is *unpriced*: it is
   excluded from every cost total and from `costs.csv`, and counted only in `unpriced`.
   It is still a surviving request and is counted in `requests`. Pricing it at zero is the
   bug this drill exists to prevent.
6. **Money is written with exactly 6 decimal places**, in the CSV and in the JSON
   (`7.5` is written `7.500000`).

## Output

Write exactly these files to `$OUT`:

1. **`out/costs.csv`** — header `request_id,model,cost`. One row per **priced** request,
   sorted by `request_id` ascending, then `model` ascending (both compared as strings).
   `cost` has exactly 6 decimals.
2. **`out/summary.json`** — an object with exactly these keys:
   - `requests` — surviving requests (int, including unpriced ones and repeats)
   - `priced` — requests with a row in `costs.csv` (int)
   - `unpriced` — requests whose model had no rate (int)
   - `total_cost` — number, sum of the rounded per-request costs, 6 decimals
   - `by_model` — object mapping model name to that model's total cost (number, 6
     decimals). Only priced models appear. Keys sorted ascending.

## Messes to expect

- `r05`/`r07` use models (`gpt-x`, `haiku-mini`) that are not in `pricing.csv`: they are
  `unpriced`, not free, and get no `costs.csv` row
- `r04` has no `output_tokens`: cost is the input half only
- `r03` is `cached: true`: its 10 000 input tokens bill at 0.1 × the `large` input rate
- `r08` costs 0.009615 — sub-cent precision survives to 6 decimals
- `r06` appears twice (once `small`, once `medium`): two rows, both billed
- a blank line, a broken JSON line, a JSON array, and an object with no `model` are all
  junk: they are not counted anywhere

## Timebox

A few minutes. If you are past that, the approach is wrong.

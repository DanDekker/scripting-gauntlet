# 148-benchmark-leaderboard

> "Six models, three benchmarks, and the vendor scorecards all disagree because every
> benchmark uses a different scale — 85.2 percent accuracy is not comparable to 120 ms of
> latency. Normalize each suite onto 0–1, weight them the way the config says, and give me
> one ranked leaderboard."

## Input

`in/results.csv` — header `model,suite,score,metric`, one measurement per row:

```
claude-3-5,coding,85.2,accuracy
claude-3-5,speed,120.0,latency_ms
gpt-4o,coding,84.0,accuracy
gpt-4o,speed,95.0,latency_ms
```

`in/weights.json` — which suites count and how:

```json
{
  "coding": {"weight": 0.6, "higher_is_better": true},
  "speed": {"weight": 0.4, "higher_is_better": false},
  "safety": {"weight": 0.2, "higher_is_better": true}
}
```

## Rules

### 1. Reading the results

Trim every field. Skip the header row, blank lines, rows with fewer than 4 fields, and
rows whose `model` or `suite` is empty. Model names are compared **case-sensitively** after
trimming, so ` GPT-4o ` and `gpt-4o` are two different models.

Ignore any row whose `suite` is not a key of `weights.json` — that suite takes part in
nothing, not even in `total_models`… except that a model which only appears in an ignored
suite row still counts as a model that exists (it is simply never complete).

### 2. Duplicates

When the same `model` and `suite` appear more than once, the **last** row in file order
wins. There is no averaging and no fallback: if the last row's score does not parse, that
model has **no valid score** for that suite.

### 3. Valid scores

A score is valid when it parses as a decimal number: an optional sign, digits with an
optional fractional part, and an optional exponent. Negative numbers are valid — a
negative score is a real measurement, not a parse error. `abc`, `n/a` and an empty field
are not valid.

### 4. Normalization, per suite, over the valid scores of that suite

Let `min_score` and `max_score` be the smallest and largest valid score in the suite:

- `max_score == min_score` → every model with a valid score in that suite gets `1.0`
- `higher_is_better: true` → `norm = (score - min_score) / (max_score - min_score)`
- `higher_is_better: false` → `norm = (max_score - score) / (max_score - min_score)`

For a lower-is-better suite the **highest** (slowest) score therefore gets `0.0` and the
lowest gets `1.0`.

### 5. Complete models and the composite

A model is **complete** when it has a valid score for **every** suite defined in
`weights.json`. Only complete models are ranked.

```
composite = sum over defined suites of (norm * weight) / sum of all weights
```

The composite is written with exactly 4 decimals.

### 6. Ranking

Sort complete models by the **4-decimal composite** descending. Ties go to the model name
ascending (byte order). Rank is `1`, `2`, `3` … over that list, with no shared ranks.

## Output

Write exactly these files to `$OUT`:

1. **`out/leaderboard.csv`** — header `rank,model,composite_score`. One row per complete
   model, sorted by `rank` ascending. `composite_score` has exactly 4 decimals
   (`0.8983`, not `0.898`).
2. **`out/summary.json`** — an object with exactly these keys:
   - `total_models` — every distinct trimmed model name seen in a data row (int)
   - `complete_models` — models with a valid score in every defined suite (int)
   - `incomplete_models` — `total_models - complete_models` (int)
   - `top_model` — rank 1 model (string), `""` when nothing is complete
   - `winning_score` — rank 1 composite, 4 decimals (float), `0.0` when nothing is complete

## Messes to expect

- `o3-mini` has two `speed` rows (`150.0`, then `140.0`): the last one wins, so `o3-mini`
  is the **fastest** model at 140.0 and scores `0.0` on `speed`
- `deepseek-v2`'s `coding` score is `-12.5`: it is valid, it becomes the suite minimum, so
  raw `85.2` is not a `1.0`
- `mistral-small`'s `coding` score is `abc`: the model is incomplete, not zero-scored
- `gemini-pro` only has `safety`, and ` GPT-4o ` is a second model distinct from `gpt-4o`:
  both are incomplete
- `reasoning` rows are not in `weights.json`: they are ignored entirely, but the models that
  appear only there would still count
- every `safety` score is `0.90`, so `max_score == min_score` there and every complete model
  banks a flat `1.0` on that suite
- `llama-3`'s `speed` row has trailing spaces: trim, do not choke
- `claude-3-5` and `zeta-model` have identical evidence: they tie, and the tie-break is the
  model name

## Timebox

Four minutes. If you are past that, the approach is wrong.

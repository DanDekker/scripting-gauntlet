# 134-cost-allocation

> "Our agents burn tokens across a handful of projects and three roles. I have the session
> log, the price sheet, and the budget I promised my manager. Tell me what each project and
> each role actually costs, which project blew its budget, and which sessions actually
> finished clean."

## Input

- **`in/sessions.jsonl`** — one JSON object per line, one object per turn:

  ```json
  {"session_id":"s1","project":"infra","role":"planner","model":"gpt-4o","prompt_tokens":1500,"completion_tokens":250,"success":true}
  ```

  A session has many turns, so `session_id` repeats across lines.
- **`in/pricing.csv`** — header `model,prompt_per_1k,completion_per_1k`. Rates are USD per
  1000 tokens.
- **`in/budgets.json`** — an object mapping project name to a maximum spend in USD, e.g.
  `{"infra": 10.0}`. A project with no entry has **no** budget limit.

## Rules

1. **Skipping.** Blank lines, lines that are not valid JSON, and lines that parse to
   something other than a JSON object (an array, a string, a number) are skipped. Cheap to
   say, easy to get wrong: they are not turns and are not counted anywhere below.
2. **`total_turns`** counts the lines that parsed to a JSON **object**, valid or not. This
   is the number a human can audit against the file.
3. **Validation.** A parsed object is a **valid turn** if and only if, after stripping
   leading and trailing whitespace:
   - `session_id`, `project`, `role` and `model` are non-empty strings, and
   - `prompt_tokens` and `completion_tokens` are JSON integers `>= 0`.

   A string (`"900"`), a boolean, `null`, a negative number, a fractional number (`10.5`)
   or a missing field makes the turn **invalid**: it is dropped from every output and is not
   part of `valid_turns`. `role` and `model` are compared **after** trimming, so
   `"  planner  "` is the role `planner` and `"  claude-sonnet  "` is a model that can be
   priced.
4. **Cost.** `cost = (prompt_tokens / 1000) * prompt_per_1k + (completion_tokens / 1000) * completion_per_1k`,
   rounded to **6 decimals** per turn. A model with no row in `in/pricing.csv` is
   **unpriced**: its turn costs `0.000000`, still counts as a turn of its project and role,
   and is added to `unpriced_turns`.
5. **Aggregates.** Project cost and role cost are the sum of the rounded per-turn costs,
   then rounded to 4 decimals for display. `pct_spend` is that role's share of the **priced
   spend of all valid turns** (the 0.000000 unpriced turns do not move it), as a percentage
   `0.00`–`100.00`, rounded to 2 decimals; when total spend is 0 every `pct_spend` is `0.00`.
6. **Budget.** A project is over budget iff its cost is **strictly greater than** its
   budget. A project with no budget entry is never over budget.
7. **Sessions.** A session is successful iff **every** one of its valid turns has
   `success: true`. A turn whose `success` key is missing counts as `false`. Both the
   session counts consider only valid turns, so the sessions are the ones that appear in
   `in/sessions.jsonl` on a valid turn.

## Output

Write exactly these files to `$OUT`:

1. **`out/projects.csv`** — header `project,turns,cost,budget,over_budget`.
   One row per project that has at least one valid turn, sorted by `project` ascending
   (plain byte order, `-` before letters).
   - `turns` — count of valid turns in the project (int).
   - `cost` — always 4 decimals (`0.1320`, not `0.132`).
   - `budget` — 4 decimals, or the empty string when the project has no budget entry.
   - `over_budget` — `true` or `false`, lowercase.
2. **`out/roles.csv`** — header `role,turns,cost,pct_spend`.
   One row per role that has at least one valid turn, sorted by `role` ascending.
   - `cost` — 4 decimals. `pct_spend` — 2 decimals (`53.93`, not `53.9`).
3. **`out/summary.json`** — object with exactly these keys:
   - `total_turns` (int) — lines that parsed to an object
   - `valid_turns` (int)
   - `unpriced_turns` (int)
   - `total_spend` (float, rounded to 4 decimals)
   - `over_budget_projects` (int)
   - `successful_sessions` (int)
   - `total_sessions` (int)

## Messes to expect

- Two models in the log have no price row. They are turns, not errors: they land in
  `unpriced_turns` and drag `pct_spend` denominators not at all.
- `"  900"`-style strings and a `10.5` token count are invalid turns, not `900` and `10`.
- A session whose *second* turn has `success: false` fails as a whole, even though its
  first turn succeeded.
- A project that exists only in the budget file has no row; a project that exists only in
  the log still gets a row with an empty budget.
- `cost` of `0.0000` is a real row, not a reason to skip it.

## Timebox

A few minutes. If you are past that, the approach is wrong.

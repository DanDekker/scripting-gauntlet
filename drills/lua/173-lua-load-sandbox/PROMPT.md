# 173-lua-load-sandbox

> "Users send us arithmetic. One of them sent `os.time()` and another sent a bare string.
> Evaluate them, but only the six functions we allow, and say exactly what went wrong."

## Input

`in/exprs.txt` — one Lua **expression** per line. Blank lines and `#` comments are skipped.

## Rules

1. Each line is an expression, not a statement: compile it as `return <expr>`.
2. Compile with `load(chunk, "expr", "t", env)` where `env` is a sandbox table that
   contains exactly `floor`, `ceil`, `abs`, `min`, `max`, `sqrt` (from `math`) and nothing
   else. Reading any other global name raises `unknown name: <name>`.
3. Classify each expression:
   - `syntax` — `load` returned no function
   - `runtime` — the compiled chunk raised when called
   - `not_number` — it evaluated, but the value is not a number
   - `ok` — it evaluated to a number
4. `detail` is the value (`tostring`) for `ok` and `not_number`, and the **normalised
   error message** for `syntax` and `runtime`: drop a leading `[string "expr"]:<line>: `
   prefix, keep the rest verbatim.

## Output

Write exactly these files to `$OUT`:

1. **`out/results.csv`** — header `expr,status,detail`, one row per expression in input
   order. Quote a field that contains a comma or a double quote. The expression is echoed
   as written.
2. **`out/summary.json`** — an object with exactly these keys: `lines`, `ok`, `syntax`,
   `runtime`, `not_number`. One compact JSON object:
   `{"lines":11,"ok":5,"syntax":1,"runtime":4,"not_number":1}`.

## Messes to expect

- `os.time()` must be refused by name, not evaluated — the sandbox is the whole point
- `2 +` fails at compile time, so `load` returns `nil` and a message
- `1 // 0` compiles and then raises inside `pcall`
- `1 / 0` is `inf` and **is** a number: it is `ok`, not an error
- `'a' .. 'b'` evaluates to the string `ab`: `not_number`
- `max(1, 5, 2)` contains commas, so the CSV field needs quoting

## Timebox

Six minutes. Sandbox first, then classify: compile failure, call failure, non-number.

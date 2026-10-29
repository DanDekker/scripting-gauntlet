# 192-lua-env-sandbox

> "Our metric rules engine allows operators to define computed fields as Lua expressions.
> We must evaluate these expressions in a sandboxed environment: safe math and string operations
> must succeed, syntax errors must be caught at load time, and attempts to invoke forbidden
> system modules (like `os` or `io`) must fail gracefully."

## Input

`in/expressions.txt` — pipe-separated `<id>|<expr>`:

```
1|math.abs(-42)
2|string.upper(name)
3|os.execute('rm -rf /')
4|x * 2 + y
5|math.sqrt(9) + * 2
6|io.open('/etc/passwd')
```

Blank lines and `#` comments are skipped.

## Environment & Variables

The sandbox environment must only contain:
- `math` table with: `abs`, `min`, `max`, `sqrt`, `floor`
- `string` table with: `lower`, `upper`, `sub`
- `tonumber`, `tostring`
- Context variables: `name = "alice"`, `x = 10`, `y = 5`

No access to `os`, `io`, `debug`, `package`, `load`, or standard global `_G`.

## Rules

For each expression in `in/expressions.txt`:
1. Compile with `load("return (" .. expr .. ")", "expr", "t", env)`.
2. If compilation fails (returns `nil`):
   - `status = compile_error`
   - `result = ""`
3. If compilation succeeds, execute the function inside `pcall`:
   - If execution succeeds: `status = ok`, `result = tostring(res)`
   - If execution fails (e.g. attempting to index nil `os` or `io`): `status = runtime_error`, `result = ""`
4. Integers and whole numbers should format cleanly via `tostring`.

## Output

Write exactly these files to `$OUT`:

1. **`out/results.csv`** — header `id,status,result`, in input order.
2. **`out/summary.json`** — keys `expressions`, `ok`, `runtime_error`, `compile_error`.
   One compact JSON object:
   `{"expressions":6,"ok":3,"runtime_error":2,"compile_error":1}`.

## Messes to expect

- `os.execute` must not be executed; accessing `os` resolves to `nil` and raises a runtime error when called.
- Malformed syntax (`+ *`) must be caught as `compile_error`.

## Timebox

Four minutes. Construct a table with safe functions and pass it to `load(..., "t", env)`.

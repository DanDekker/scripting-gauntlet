# 190-ps1-exitcode-trap

> "Our deployment pipeline runs a sequence of steps via native tool invocations. The operator
> wrapped the calls in `try { ... } catch { ... }` with `$ErrorActionPreference = 'Stop'`, but
> failed commands never entered the `catch` block and the pipeline reported all steps as success."

## Input

`in/steps.csv` — header `id,action,arg,code`:

```
id,action,arg,code
1,ping,gateway,0
2,fetch,https://example.com/asset,10
3,auth,token_alpha,0
4,sync,database,42
5,cleanup,temp_cache,0
```

## Rules

1. For each record in `in/steps.csv`, execute the native process:
   `python3 -c "import sys; sys.exit(int(sys.argv[1]))" <code>`
2. Determine `status`:
   - If exit code is `0`: `success`
   - If exit code is non-zero: `failed`
3. Inspect `$LASTEXITCODE` directly after execution; do not assume `try/catch` will intercept native binary exit codes.
4. Export results in step order.

## Output

Write exactly these files to `$OUT`:

1. **`out/results.csv`** — header `id,action,code,status`.
2. **`out/summary.json`** — keys `total_steps`, `succeeded`, `failed`. One compact JSON object:
   `{"total_steps":5,"succeeded":3,"failed":2}`.

## Messes to expect

- Wrapping native commands in `try/catch` with `$ErrorActionPreference = 'Stop'` does **not** catch non-zero exit codes in PowerShell without explicitly checking `$LASTEXITCODE`.
- Both `$code` and `$status` must reflect the actual outcome.

## Timebox

Four minutes. Check `$LASTEXITCODE` after each native command.

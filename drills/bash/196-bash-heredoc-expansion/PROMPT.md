# 196-bash-heredoc-expansion

> "Our service orchestrator generates per-service wrapper scripts using bash heredocs.
> The generator interpolated build-time ports and service names, but forgot to escape `\$1`
> and `\$ACTION`, causing all generated scripts to ignore runtime command line arguments."

## Input

`in/services.csv` — header `name,port,env,health_path`:

```csv
name,port,env,health_path
api,8080,prod,/healthz
auth,9000,staging,/status
worker,5000,prod,/ping
```

## Rules

1. For each service row in `in/services.csv`, generate an executable bash script in `$OUT/<name>_runner.sh`.
2. The generated script must have the following structure:
   - Interpolate build-time values: service name, port, env, health_path.
   - Preserve runtime variables: `ACTION="\${1:-status}"`, `case "\$ACTION" in ...`.
   - On `start`: output `Starting <name> in <env> on port <port>...` and exit 0.
   - On `check`: output `Checking health at http://127.0.0.1:<port><health_path>` and exit 0.
   - On anything else: exit 1.
3. Make the generated script executable (`chmod +x`).
4. Execute each script twice:
   - `<script> start` (expect exit 0)
   - `<script> check` (expect exit 0)
5. Record execution results in `out/manifest.csv`.

## Output

Write exactly these files to `$OUT`:

1. **`out/<name>_runner.sh`** — generated runner script for each service.
2. **`out/manifest.csv`** — header `service,action,exit_code,output`, in service order (start, then check).
3. **`out/summary.json`** — keys `services`, `total_runs`, `success`. One compact JSON object:
   `{"services":3,"total_runs":6,"success":6}`.

## Messes to expect

- In an unquoted heredoc `cat <<EOF`, `\$1` and `\$ACTION` must be escaped with a backslash (`\`), otherwise bash evaluates them as the generator's empty `$1`.

## Timebox

Four minutes. Use `cat <<EOF` with escaped `\$1` and `\$ACTION`.

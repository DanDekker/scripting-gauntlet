# 191-bash-assoc-presence

> "Our service configuration loader parses key=value pairs into an associative array.
> Some keys are deliberately set to empty strings (e.g. `DEBUG=`), but the validator used
> `[[ -n ${config[$k]} ]]` and erroneously treated them as missing keys."

## Input

- `in/config.txt` — key=value pairs. Blank lines and `#` comments are skipped.
- `in/queries.txt` — list of keys to query, one per line.

```
HOST=api.internal
PORT=8080
DEBUG=
TIMEOUT=0
CACHE_DIR=
```

## Rules

1. Parse `in/config.txt` into a bash associative array (`declare -A config`).
   - A line `KEY=` sets key `KEY` to the empty string `""`.
2. For each key in `in/queries.txt` (in order):
   - If the key is not in `config`: `status = missing`, `value = ""`
   - If the key exists and its value is `""`: `status = empty`, `value = ""`
   - If the key exists and its value is non-empty: `status = set`, `value = <value>`
3. Check key presence using `[[ -v config[$key] ]]`.

## Output

Write exactly these files to `$OUT`:

1. **`out/results.csv`** — header `key,status,value`.
2. **`out/summary.json`** — keys `queries`, `set`, `empty`, `missing`. One compact JSON object:
   `{"queries":6,"set":2,"empty":2,"missing":2}`.

## Messes to expect

- `DEBUG=` has an empty value, which must be reported as `status = empty`, not `missing`.
- `TIMEOUT=0` is a valid set value `"0"`.

## Timebox

Four minutes. Use `[[ -v config[$k] ]]` to detect key existence.

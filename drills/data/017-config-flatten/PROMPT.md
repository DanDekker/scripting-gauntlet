# 017-config-flatten

> "Config has nested sections and a list. Flatten it so I can diff two versions."

## Task

`in/app.yaml` is a small config file:

```yaml
name: scriptdeck
version: 3
features:
  - api
  - scrape
limits:
  timeout: 30
  retries: 2
```

## Rules

1. Flatten to **dotted paths**: a key inside `limits` becomes `limits.timeout`.
2. A section header (a key with no value) opens a scope; its children are prefixed
   with it.
3. A list becomes **indexed keys**: `features.0`, `features.1`, in file order.
4. Values keep their type: `3` is a number, `scriptdeck` is a string.

## Output

**`out/flat.json`** — a single JSON object mapping paths to values:

```json
{"name": "scriptdeck", "version": 3, "features.0": "api", "limits.timeout": 30}
```

**`out/summary.json`** — exactly one key: `keys` (how many flattened keys).

## Messes to expect

- a list of two items, which becomes two keys
- a number that must stay a number and not become a string

## Timebox

4 minutes. Track indentation with a stack; `jq` can do the JSON part.

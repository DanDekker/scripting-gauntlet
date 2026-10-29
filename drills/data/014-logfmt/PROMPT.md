# 014-logfmt

> "App logs are in logfmt. Which endpoints are slow?"

## Task

`in/app.log` has one record per line in logfmt: space-separated `key=value` pairs.

```
ts=2026-10-29T10:00:01Z level=info msg="request served" path=/api/users dur=12ms status=200
```

## Rules

1. A value may be **quoted** with `"` — then it may contain spaces. Unquoted values run
   to the next space.
2. `dur` carries a unit suffix (`ms`). Strip it and treat the rest as an integer.
3. `level` is one of `info`, `warn`, `error`.
4. Sort by `dur` **descending**, ties broken by `path` **ascending**.

## Output

**`out/requests.csv`** — header, then one row per record:

```
path,status,dur_ms
/api/orders,504,3000
```

**`out/summary.json`** — exactly four keys: `lines` (records parsed), `errors`, `warns`,
`infos` (counts by level).

## Messes to expect

- a quoted value containing spaces
- two records with the same duration

## Timebox

4 minutes. Write the tokenizer once; `shlex` in python does it for you.

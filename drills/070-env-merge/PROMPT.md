# 070-env-merge

> "Our app reads two env files: the committed defaults and my machine's overrides.
> Tell me the config I actually get, and how much my override file changed."

## Task

`in/base.env` is the committed default; `in/local.env` is the machine override. They are
plain `KEY=VALUE` files applied in that order - a later file replaces an earlier key.

## Rules

1. Read `base.env` first, then `local.env`.
2. Ignore blank lines and lines whose first non-space character is `#`.
3. A line may start with `export ` followed by exactly one space.
4. Split on the **first** `=`. The key is trimmed and must match `[A-Za-z_][A-Za-z0-9_]*`;
   otherwise print `<file>:<line>: bad key` on stderr and exit non-zero.
5. The value is trimmed:
   - if it starts with `"` or `'`, everything up to the matching close quote is the value,
     literally (a `#` inside the quotes is data); an unclosed quote is an error;
   - otherwise the first `#` starts a comment, so the value ends before it.
6. A key may repeat; the last assignment wins. Quote characters are not part of the value.

## Output

- `out/config.json` - one object, key to string value, keys sorted ascending, every value a
  string (`""` stays `""`).
- `out/summary.json` - exactly four integers: `files` (files read), `keys` (distinct keys in
  the merged config), `overridden` (keys assigned in both files), `empty` (keys whose final
  value is empty).

## Messes to expect

- a trailing comment after a quoted value
- a quoted value containing `#`
- `export` in front of a key
- an empty value, and a key overridden by the later file

## Timebox

3 minutes. Let the parser walk each file once, writing `key value` into a map.

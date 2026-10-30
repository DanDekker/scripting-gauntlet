# 206-perl-exists-autoviv

> "The config audit started listing a `cache` section that nobody had ever set. The
> audit checked `if (exists $cfg{$section}{$key})` — and a nested `exists` creates the
> intermediate hash on the way, so merely asking the question added a section."

## Input

`in/base.conf` — the base configuration:

```text
# base configuration
[core]
host=localhost
port=8080

[limits]
timeout=30
```

`in/wanted.conf` — one `section.key` per line:

```text
core.host
core.port
core.timeout
limits.timeout
cache.ttl
```

## Rules

1. Parse `in/base.conf` into a hash of sections, each holding its own keys.
   - A line `[name]` starts a section.
   - A line `key=value` adds a key to the current section.
   - Blank lines and lines starting with `#` are ignored.
2. For each line of `in/wanted.conf` (in order, skipping blank lines and `#`
   comments), split at the **first** `.`: the part before it is the section, the
   part after it is the key.
3. Report `present` when the base config holds that key in that section, and
   `missing` otherwise.
4. **Your checks must not change the config.** A section that is not in
   `in/base.conf` must not appear in the config afterwards.
5. **`out/missing.csv`** — header `index,section,key,status`. One row per wanted
   line, in file order, `index` starting at 1.
6. **`out/dump.csv`** — header `section,keys`. The base config's sections,
   alphabetically, with the number of keys each holds — as the config stands after
   your checks.
7. **`out/summary.json`** — keys `wanted`, `present`, `missing`, `sections`. One
   compact JSON object. `sections` is the number of sections in the config after
   your checks.

## Messes to expect

- `exists $cfg{$sec}{$key}` creates `$cfg{$sec}` when the section is missing. The
  check looks harmless and is not: it adds an empty section to the config.
- `exists $cfg{$sec} && exists $cfg{$sec}{$key}` asks without creating.

## Timebox

Five minutes.

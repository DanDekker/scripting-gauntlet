# 219-perl-undef-vs-empty

> "The config audit reported `timeout` as empty and `retries` as empty too — but `retries`
> was never in the file at all. The audit read the value with `// ''` and then asked
> whether it was empty, so a missing key and a key set to nothing looked the same."

## Input

`in/config.ini` — `key=value` lines:

```text
host=db.local
port=5432
timeout=
```

`in/wanted.txt` — the settings to report on, one per line:

```text
host
port
timeout
retries
```

## Rules

1. Read `in/config.ini` into a hash of settings: the key is the text before the first
   `=`, the value is everything after it. A value may be empty (`timeout=`).
2. Read `in/wanted.txt`, one setting name per line, in order.
3. For each wanted setting, report its status:
   - `set` — the setting is in the config and its value is not empty;
   - `empty` — the setting is in the config and its value **is** empty;
   - `missing` — the setting is **not in the config at all**.
4. **`out/settings.csv`** — header `index,key,status,value`. One row per wanted setting,
   in file order, `index` starting at 1. `value` is the setting's value for a `set`
   setting, and empty for `empty` and `missing`.
5. **`out/summary.json`** — keys `wanted`, `set`, `empty`, `missing`. One compact JSON
   object.

## Messes to expect

- A setting that is not in the file reads as `undef`. `undef` is **not** the empty
  string, but `undef eq ''` is true (and warns), so a missing setting looks empty.
- `my $v = $cfg{$key} // '';` turns a missing setting into the empty string, which
  erases the difference you are trying to report.
- `exists $cfg{$key}` is the test that tells the two apart.

## Timebox

Five minutes.

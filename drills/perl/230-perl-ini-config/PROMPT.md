# 230-perl-ini-config

> "Our deploy scripts read service parameters from INI files. A recent change added
> inline comments like `timeout = 30 ; socket seconds` and environments without an explicit
> timeout failed with `invalid integer '30 ; socket seconds'`."

## Input

- `in/config.ini` — INI file with sections:
  - Comments start with `#` or `;` and can appear on their own lines or inline after a value.
  - Section headers have the format `[section]`.
  - Properties have the format `key = value`.
  - Empty lines and pure comment lines are ignored.
  - The `[default]` section holds baseline values inherited by other sections.

```ini
# Global daemon settings
[default]
retries = 3
timeout = 30 ; default socket timeout
log_level = info
notify = ops@example.com
buffer_kb = 64

; Staging environment overrides
[staging]
timeout = 60
log_level = debug

[production]
retries = 5
notify = oncall@example.com ; pager alerts
buffer_kb = 256
```

- `in/queries.csv` — header `section,key`:
  List of queries to resolve in file order.

```csv
section,key
staging,timeout
staging,retries
staging,log_level
staging,buffer_kb
production,retries
production,timeout
production,notify
production,missing_key
qa,timeout
default,notify
```

## Rules

1. Parse `in/config.ini`:
   - Strip comments starting with `#` or `;` from each line, including any whitespace
     immediately preceding the comment.
   - Strip leading and trailing whitespace from section names, keys, and values.
   - Skip empty lines.
2. Resolve queries from `in/queries.csv` in file order:
   - If the requested `section` defines `key`, use that value; `source` is `section`.
   - Otherwise, if `[default]` defines `key`, use that value; `source` is `default`.
   - If neither defines `key` (or if the section does not exist and `[default]` lacks the key),
     the value is `MISSING` and `source` is `none`.
3. **`out/answers.csv`** — header `section,key,value,source`.
   - One row per query, in query order.
4. **`out/summary.json`** — keys `queries`, `section`, `default`, `missing`.
   - `queries` — total queries resolved.
   - `section` — queries resolved from the specific section.
   - `default` — queries resolved via fallback to `[default]`.
   - `missing` — queries where the key was `MISSING`.
   - Emit as a single compact JSON object.

## Messes to expect

- Inline comments: values may be followed by ` ; comment` or ` # comment`. The comment
  and preceding whitespace must not be included in the value.
- Section inheritance: querying a section that does not exist (like `qa`) must still
  fall back to `[default]` without autovivifying garbage or crashing.

## Timebox

Five minutes.

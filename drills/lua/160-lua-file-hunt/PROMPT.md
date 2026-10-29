# 160-lua-file-hunt

> "Find every log file over 100 bytes in this tree. Last time the search also returned
> 'myblog', so whatever matched must actually end in '.log'."

## Input

`in/hunt/` — a directory tree holding files of known sizes, including a directory named
`archive` and a dot-directory, both of which are out of scope.

The query is fixed:

- pattern: **`*.log`**
- minimum size: **100 bytes**

## Rules

1. Walk `in/hunt` recursively. A directory named **`archive`**, or whose name begins with
   `.`, is **excluded**: nothing below it is considered, and its files are not scanned.
2. Only **regular files** count. A symlink is neither followed nor counted.
3. Match the **base name** — not the path — against the pattern, **case-sensitively**, with
   glob semantics:
   - `*` matches zero or more characters
   - `?` matches exactly one character
   - every other character is **literal**: the `.` in `*.log` is a dot, and so are `-`,
     `%`, `+` and `(`. `*.log` matches `app.log` and must **not** match `myblog` or
     `c.log.old`.
4. Keep a file when its base name matches **and** its size is at least 100 bytes.
5. `scanned` counts every regular file considered, whether or not it matched.

## Output

Write exactly these files to `$OUT`:

1. **`out/found.csv`** — header `path,size`, one row per kept file, `path` relative to
   `in/hunt`, sorted by `size` **descending**, ties broken by `path` ascending in byte
   order.
2. **`out/summary.json`** — an object with exactly these keys:
   - `matched` — how many files were kept (int)
   - `bytes` — the total size of the kept files (int)
   - `scanned` — how many regular files were considered (int)

   Print it as one compact JSON object: `{"matched":2,"bytes":240,"scanned":6}`.

## Messes to expect

- `myblog` looks like a log file to a careless pattern translation; it is not one
- `c.log.old` ends in `.old`, so it does not match `*.log`
- `b.log` matches the pattern but is only 90 bytes
- `archive/e.log` and `.hidden/f.log` are large and would match, but both directories are
  excluded
- `g.txt` is large but the pattern rules it out

## Timebox

Four minutes. Translate the glob to a Lua pattern and escape the literal characters first;
`gsub("%*", ".*")` alone turns `*.log` into `.*.log`, which matches `myblog`.

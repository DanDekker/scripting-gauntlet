# 117-i18n-keys

> "The app shipped and half the screen says `app.fresh` instead of words. Which keys does
> the code call that the locale file never got, and which locale keys is nobody using?"

## Input

- `in/src/` — a directory of source files, at least four of them, with translation calls in
  two shapes: `t("some.key")` and `i18n.t('other.key')`. Files may sit in subdirectories.
- `in/locale.json` — an object mapping locale keys to translated strings:
  `{"some.key": "Hello", "other.key": "World"}`

## Rules

1. **What counts as a call.** The identifier `t`, or the identifier `i18n.t`, immediately
   followed by `(`, then a quoted string literal (`'` or `"`), then `)`. Whitespace —
   including a newline, so a call may span two lines — is allowed between the `(`, the
   literal and the `)`. The literal must be closed on one line and no escape processing is
   done: the key is the raw text between the quotes. The identifier must stand alone — the
   character before it may not be a letter, digit, `_`, `$` or `.`, so `split(` and `x.t(`
   are not calls.
2. **Not a call.** A `t(` inside a line comment (`//` or `#`, to end of line) or inside a
   quoted string (`'`, `"` or a backtick) is not a call. `t("key",)` — a comma between the
   literal and `)` — is not a call either.
3. **Occurrences, not keys.** Every call is one row. A key used twice in the same file is
   two rows; the same key in two files is two rows. The row's `line` is the line where the
   `t` / `i18n.t` token starts, even when the key itself is on the next line.
4. **present / missing.** A key is `present` when it is a key of `in/locale.json`, even if
   its value is empty or is not a string. Otherwise it is `missing`.
5. **unused.** A locale key that appears in no call anywhere in `src/` is unused, with
   `reason` `unused`. An unused key may still be invalid — it is reported in both places.
6. **invalid.** A locale entry whose value is not a JSON string, or is the empty string, is
   invalid. Invalid entries are counted only; they get no row of their own.

## Output

Write exactly these files to `$OUT`:

1. **`out/keys.csv`** — header `file,line,key,status`. One row per call occurrence, files
   sorted by path ascending (byte order) and, inside a file, in line order as the calls
   appear. `file` is the path of the source file relative to `in/src/`, with `/` separators
   (`app.js`, `ui/modal.js`). `line` is 1-based. `status` is exactly `present` or `missing`.
2. **`out/unused.csv`** — header `key,reason`. One row per locale key used in no call,
   sorted by `key` ascending (byte order), each with `reason` `unused`.
3. **`out/summary.json`** — an object with exactly these keys:
   - `files` — files under `src/`, recursively (int)
   - `calls` — call occurrences, i.e. the number of rows in `keys.csv` (int)
   - `distinct` — distinct keys used (int)
   - `missing` — distinct keys that were used but are absent from the locale file (int)
   - `unused` — locale keys used in no call (int)
   - `invalid` — locale entries whose value is not a non-empty string (int)

## Messes to expect

- `app.js` has `// t("commented.key")` and `const decoy = 't("not.a.call")'` — neither is
  a call, so `commented.key` and `not.a.call` appear nowhere and are not reported
- `app.js`'s `t(` for `app.fresh` spans two lines; the row's line is the line of the `t`
- `header.js` calls `header.tagline` twice: two rows with the same key
- `legacy.py` puts two calls on one line and uses `#` for its comment; `_(` is not `t(`
- `header.js` ends with `t("header.comma", )` — a comma means it is not a call
- `legacy.py`'s `app.title` is also used by `app.js`: the same key in two files is two rows
- `locale.json` has `"button.close": ""` (invalid, but `present`) and
  `"legacy.count": 42` (invalid, but `present`)
- `locale.json` has `orphan.key` and `zzz.orphan`, which no source file calls
- `src/empty.js` has no calls at all but still counts in `files`

## Timebox

Four minutes. If you are past that, the approach is wrong.

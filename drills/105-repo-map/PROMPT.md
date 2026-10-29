# 105-repo-map

> "Before an agent writes a line it should know what is in this repo. Give me the map: what
> kinds of files live here, how many bytes each kind owns, and which top-level directories
> hold them. And do not count the noise."

## Input

`in/tree/` — a directory tree, at least three levels deep.

Two paths inside `in/tree/` (`tree/.git/config` and
`tree/__pycache__/main.cpython-311.pyc`) are created by this drill's `setup.py` before the
solution runs, because git cannot store a nested `.git` directory or a `*.pyc` file.
Everything else is committed under `fixtures/tree/` as plain text.

## Rules

1. **Walk the tree once.** Skip any directory whose name is exactly `node_modules`,
   `__pycache__`, `.git` or `dist` — do not descend into it, and nothing inside it is
   counted or skipped-on-its-own. Skip any **file** whose name starts with `.` (a hidden
   file): it is not counted, and it increments `skipped` by one.
   A dot-prefixed *directory* is **not** skipped unless it is one of those four names, so
   `.github/workflows/ci.yml` is a counted file.
2. **Kind** is decided from the file's name, first rule that matches wins:
   1. `test` — the **stem** ends in `.test` or `_test`. The stem is the basename with its last
      extension removed (`a.test.ts` -> `a.test`, `a_test.py` -> `a_test`). This rule beats
      every other rule.
   2. `config` — the basename is exactly one of `package.json`, `Makefile`, `pyproject.toml`,
      `setup.cfg`, `tsconfig.json` (case-sensitive).
   3. `py` — last extension `py`. `js` — `js`, `mjs` or `cjs`. `ts` — `ts` or `tsx`.
      `md` — `md`. Extensions compare lowercased, so `util.PY` is `py`.
   4. `other` — everything else: no extension, an unknown extension, or a double extension
      whose last component is unknown (`notes.md.bak` is `other`).
   A double extension always classifies by its **last** extension, except that the `test`
   rule runs first.
3. **Top-level directory.** For a counted file, `dir` is the first path component under
   `in/tree/`. A file directly inside `in/tree/` has `dir` `(root)`.
4. **Empty directories vanish.** A directory that ends up holding no counted file is not a
   row anywhere: `in/tree/empty/` holds only a hidden file, so it does not exist for the map.

## Output

Write exactly these files to `$OUT`:

1. **`out/map.csv`** — header `kind,files,bytes`. One row per kind with at least one counted
   file, sorted by `kind` ascending in byte order (`LC_ALL=C sort`). `files` is the count,
   `bytes` is the total size in bytes of that kind's files.
2. **`out/dirs.csv`** — header `dir,files`. One row per top-level directory with at least one
   counted file, sorted by `dir` ascending in byte order. `dir` is `(root)` for files sitting
   directly in `in/tree/`.
3. **`out/summary.json`** — an object with exactly these keys, all ints:
   - `files` — counted files
   - `bytes` — total size of counted files
   - `skipped` — files skipped by the hidden-file rule (only that rule; files inside a skipped
     directory are never visited and count nowhere)
   - `dirs` — number of rows in `out/dirs.csv`
   - `largest` — size in bytes of the largest counted file

## Messes to expect

- `src/util.PY` is a python file; the extension is lowercased before it is compared
- `src/lib/a.test.ts` is `test`, not `ts`; `web/vendor/a_test.py` is `test`, not `py`
- `docs/notes.md.bak` is `other` — the last extension is `bak`
- `scripts/deploy` has no extension and is `other`
- `Makefile` and `package.json` are `config`, not `other`
- `.github/workflows/ci.yml` is counted (`other`, top-level `.github`) because `.github` is
  not one of the four skipped directory names
- `empty/` contains only `.gitkeep`, so it has no row; `.gitkeep` still counts in `skipped`
- nothing under `node_modules/`, `dist/`, `__pycache__/` or `.git/` is counted, and those
  files are not in `skipped` either
- `in/tree/.env` and `in/tree/src/.env.example` are hidden files: `skipped`, not counted

## Timebox

Four minutes. If you are past that, the approach is wrong.

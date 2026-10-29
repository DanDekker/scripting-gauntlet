# 104-test-selection

> "CI takes eleven minutes and we run every test on every push. Given this change set and
> the import graph, which test files actually need to run? And be honest about the paths you
> could not place."

## Input

`in/changes.txt` — one changed source path per line, e.g. `src/parser.py`.

`in/graph.csv` — a CSV with the header `module,imports`. Each row is one edge: `module`
imports `imports`. One import per row, so a module that imports three things has three rows.

`in/changes.txt` is messy in realistic ways: trailing whitespace on a path, blank lines, a
path repeated twice (the same path, once with trailing spaces), a path whose module is not in
the graph at all, and a path whose module only ever appears as an *import target*.

`in/graph.csv` is messy too: a module that imports itself, a duplicate edge row, a row whose
`imports` value is blank, and an import of a module that never appears in the `module` column.

## Rules

1. **The graph.** Read `graph.csv` as directed edges `module -> imports`. Strip the header
   row. Trim whitespace around both fields. A row with an empty `module` is ignored; a row
   with an empty `imports` is ignored; a row where `module == imports` is ignored (a module
   that imports itself adds nothing). Duplicate edges collapse to one.
2. **Keys.** A module is a **key** when it appears in the `module` column of at least one
   non-header row with a non-empty `module` — even if that row's `imports` is blank. A module
   that only ever appears in the `imports` column is *not* a key: it is a leaf with no
   outgoing edges.
3. **Closure.** The transitive closure of a module is that module itself plus every module
   reachable from it by following imports, transitively. `closure(parser)` for
   `parser -> lexer`, `lexer -> tokens` is `{parser, lexer, tokens}`.
4. **Tests.** A test file is a graph module whose name begins with `tests/`. Its **path** is
   that module name (`tests/parser.py`). A test file `tests/<name>.py` is treated as
   importing the module `<name>`, where `<name>` is the basename with its last extension
   removed (`tests/parser.py` -> `parser`). If `<name>` is not a key, the test imports nothing
   and can never be selected.
5. **Changed modules.** A changed path names a module: take the basename, strip the last
   extension, so `src/parser.py` -> `parser`. An extension is only stripped when the last
   `.` is not the first character of the basename (`.env` stays `.env`). Trim whitespace from
   each line and drop blank lines before doing this. Two paths that name the same module are
   two changes.
6. **Known vs unknown.** A change is **known** when its module is a key, **unknown**
   otherwise. Every distinct changed path is classified exactly once, so
   `known + unknown == changes`. Unknown changes select nothing.
7. **Selection.** A test is selected when at least one *known* changed module is in the
   closure of the module the test imports. Dedupe the change list first: a path listed twice
   is one change, not two.

## Output

Write exactly these files to `$OUT`:

1. **`out/selected.txt`** — the selected test paths (the graph module names, e.g.
   `tests/parser.py`), one per line, sorted ascending in byte order (`LC_ALL=C sort`). No
   header, no blank lines. If nothing is selected, the file is empty.
2. **`out/summary.json`** — an object with exactly these keys, all ints:
   - `changes` — distinct changed paths after trimming and deduping
   - `known` — distinct changed paths whose module is a key
   - `unknown` — distinct changed paths whose module is not a key
   - `tests` — test files considered
   - `selected` — tests in `out/selected.txt`
   - `unused` — test files not selected

## Messes to expect

- `src/parser.py` appears twice, the first copy with trailing spaces: it is **one** change
- `src/missing_leaf.py` names `missing_leaf`, which appears only in the `imports` column: it
  is a key? No — it is unknown, and it selects nothing
- `src/ghost.py` names a module that is nowhere in the graph: unknown
- the `report,report` row is a self-import and must be ignored, not followed forever
- the `formatter,` row (blank import) still makes `formatter` a key; the blank import is not
  a module and must never enter a closure
- `parser,lexer` appears twice: one edge
- `tests/legacy.py` imports `legacy`, which is not a key, so it is never selected
- `tests/config.py` is only selected by a change to `config`; a change to `parser` does not
  reach it

## Worked example

With the change set `src/parser.py`, `src/registry.py`, `src/ghost.py`,
`src/missing_leaf.py` the answer is the four tests whose closure holds `parser` or
`registry`, plus two tests left over.

## Timebox

Five minutes. If you are past that, the approach is wrong.

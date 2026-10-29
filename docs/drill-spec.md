# Drill spec

A drill is a directory under `drills/` containing a task, its input, a grader, and one
or more solutions. `harness/run.py` is the only thing that runs them.

## Layout

```
drills/001-csv-rollup/
├── drill.toml       metadata (TOML, parsed with stdlib tomllib)
├── PROMPT.md        the task, as you'd actually receive it
├── fixtures/        copied wholesale into <work>/in/
├── mock/            optional local HTTP server (api-probing drills)
├── verify.py        def verify(io) -> list[str]
└── solutions/
    ├── solve.bash
    ├── solve.py
    └── solve.lua
```

## drill.toml

```toml
id = "001-csv-rollup"     # must equal the directory name
family = "data-wrangling" # data-wrangling | api-probing | web-scraping | file-hygiene | text-munging
title = "Dedupe and roll up a dirty orders CSV"
difficulty = 2             # 1 trivial .. 5 hard
timebox = 240              # seconds a competent scripter needs. part of the spec.
teaches = ["dedupe by key", "awk associative arrays"]
mock_server = "mock/server.py"  # optional, relative to the drill dir
```

## The runtime contract

For every `solutions/solve.<ext>` the harness:

1. creates a fresh temp dir, copies `fixtures/` to `<work>/in/`, creates `<work>/out/`
2. exports `IN`, `OUT`, `WORK` (absolute) and, if `mock_server` is set, `PORT` and `API_BASE`
3. starts the mock server and waits for the port
4. runs the interpreter for `<ext>` with `cwd=<work>` and a timeout
5. tears the mock down, then calls `verify(io)` — a non-zero exit short-circuits to FAIL

If `drill.toml` declares a `mock_server`, the harness starts it with `PORT` in the
environment and expects it to bind `127.0.0.1:$PORT`. The solution talks to it via
`$API_BASE`. This keeps network drills offline and deterministic.

### Interpreters

| ext | command |
| --- | --- |
| `.bash`, `.sh` | `bash` |
| `.zsh` | `zsh` |
| `.py` | the harness's own python |
| `.lua` | `lua` |
| `.ps1` | `pwsh -NoProfile -NonInteractive -File` |
| `.js` | `node` |
| `.rb` | `ruby` |
| `.pl` | `perl` |

Add to `INTERPRETERS` in `harness/run.py` to support more. `make check` runs every drill
against every solution it ships.

## verify.py

```python
def verify(io) -> list[str]:
    """Return failures. An empty list means pass."""
```

`io` gives you `work`, `inp` (`<work>/in`), `out` (`<work>/out`), `fixtures`, `drill`,
`lang`, and `meta`. It is read-only by convention — mutating a work tree mid-verify is
how graders get flaky.

Rules for graders:

- **Assert semantics, not bytes.** Parse the output; compare row *sets*, numbers with a
  tolerance, key presence. A grader that diffs a raw file rejects correct solutions that
  sort differently.
- **One failure string per distinct problem**, phrased as the observation:
  `"out/regions.csv: expected 4 rows, got 3"`. Eleven cascading messages help nobody.
- **Never re-implement the solution in the grader.** Check the contract from `PROMPT.md`.
- **Be exact about the contract.** If the prompt says "sorted by revenue desc", the
  grader checks that order. Ambiguity here makes a drill unpassable.

## Conventions

- Solutions read fixture paths from `$IN`, never from the drill directory. They must
  work from any cwd, because the harness runs them from a temp dir.
- Solutions write only under `$OUT`. Temp files go in `$WORK` or the system temp dir.
- Non-zero exit on bad input, with the offending value on stderr.
- A drill with no solution for a language is simply skipped by `--lang` filtering; it is
  not an error to ship one language.

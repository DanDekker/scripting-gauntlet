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
├── setup.py|setup.sh optional fixture generator (one, before the solution)
├── probe.py         optional checker for a listener started by the solution
├── verify.py        def verify(io) -> list[str]
├── controls/        optional semantic negatives and manifest.toml
└── solutions/
    ├── solve.bash
    ├── solve.py
    └── solve.lua
```

## drill.toml

```toml
id = "001-csv-rollup"     # must equal the directory name
family = "data-wrangling" # one of the seven families accepted by harness/run.py
title = "Dedupe and roll up a dirty orders CSV"
difficulty = 2             # 1 trivial .. 5 hard
timebox = 240              # seconds a competent scripter needs. part of the spec.
teaches = ["dedupe by key", "awk associative arrays"]
mock_server = "mock/server.py"  # optional, relative to the drill dir
```

## The runtime contract

The accepted families are `data-wrangling`, `api-probing`, `web-scraping`,
`file-hygiene`, `text-munging`, `system-recon`, and `network-recon`.
`timebox` is an authoring goal in seconds; the runner's `--timeout` is a
separate execution limit.

For every `solutions/solve.<ext>` the harness:

1. creates a fresh temp dir, copies `fixtures/` to `<work>/in/`, creates `<work>/out/`
2. exports `IN`, `OUT`, `WORK` (absolute) and `NO_COLOR=1`
3. optionally runs `setup.py` (or `setup.sh`) to generate fixture files in `<work>/in/`
4. optionally starts a declared mock server, assigning `PORT` and `API_BASE`
5. runs the interpreter for `<ext>` with `cwd=<work>` and a timeout, then
   stops the mock server
6. optionally runs `probe.py` against a service started by the solution and
   stops that listener
7. calls `verify(io)`; an earlier
   non-zero exit or failed probe short-circuits to FAIL

If `drill.toml` declares a `mock_server`, the harness starts it with `PORT` in the
environment and expects it to bind `127.0.0.1:$PORT`. The solution talks to it via
`$API_BASE`. This keeps network drills offline and deterministic.

`probe.py` receives the same environment. A service-starting solution writes
`out/listener.pid` so the harness can stop the listener after the probe. The
runner checks the probe's exit status before loading `verify.py`.

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

## Calibration

A passing solution only shows that the verifier accepts one known answer.
For a drill claimed as calibrated, include a plausible wrong candidate in
`controls/` and declare its intended verifier diagnostic in
`controls/manifest.toml`. Run `python3 harness/calibrate.py DRILL_ID --out REPORT.json`.
The command runs every reference, checks that the negative reaches the verifier
and is rejected for the intended rule, and records source hashes. See
[Drill authoring and admission](authoring-contract.md) for the learner packet,
source lineage, and limits of each evidence stage.

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

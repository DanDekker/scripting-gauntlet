# scriptdeck

A training deck for **scripting** — the fast, dirty, in-between layer of programming.

Not systems work. Not low-level. Not web development. The work you do when you need an
answer in ten minutes: filter this data, probe that API, scrape the page, clean up the
directory, resort the files, then throw the script away.

```
~/Desktop/scriptdeck
├── docs/          what scripting is (and what it is not)
├── skills/        Agent Skills (SKILL.md) packs — loadable know-how
├── drills/        executable exercises: prompt + fixtures + verifier + solutions
└── harness/       the runner that checks them
```

## Why this exists

Most "learn to code" material trains for *building software*. Almost none of it trains
for the thing working engineers actually do between builds: **glue and probe** work.

Scripting has its own correctness standard. A script that answers the question is
correct even if it has no tests, no abstraction, and no future. A script that is
beautiful and takes three hours is wrong. That asymmetry is the whole discipline, and
it is what this deck trains.

## Quickstart

```bash
make list                 # what drills exist
make check                # run every drill against every solution
python3 harness/run.py run 001-csv-rollup --lang python
python3 harness/run.py run all --timeout 30
```

No install step. Python 3.11+ stdlib for the harness; the drills themselves need
`bash`, `zsh`, `pwsh`, `python3`, `lua`, `jq`, `curl` — each drill declares only the
interpreters it actually uses.

## Anatomy of a drill

```
drills/001-csv-rollup/
├── drill.toml       metadata: family, difficulty, timebox, what it teaches
├── PROMPT.md        the task, written the way you'd actually receive it
├── fixtures/        messy real-world input, copied into <work>/in/
├── verify.py        the grader — semantic, not golden-file diffing
└── solutions/       solve.bash, solve.py, solve.lua  (one or more languages)
```

A solution is any executable that reads `<work>/in/`, writes `<work>/out/`, and exits
non-zero on failure. The harness maps the file extension to an interpreter and runs it
in a scratch directory, so drills never touch the repo tree.

The **timebox** is part of the spec, not decoration. A drill that takes longer than its
timebox to solve is a signal you reached for the wrong tool or the wrong approach.

Full contract: [docs/drill-spec.md](docs/drill-spec.md).

## The five families

| family | the job | typical tools |
| --- | --- | --- |
| `data-wrangling` | filter, join, aggregate, reshape | awk, jq, python, lua |
| `api-probing` | hit it, page it, retry it, time it | curl + jq, urllib, Invoke-RestMethod |
| `web-scraping` | pull structure out of markup that isn't yours | python html.parser, sed/awk, lua gsub |
| `file-hygiene` | triage, rename, dedupe, resort | bash, powershell, python |
| `text-munging` | extract, normalize, summarize logs & dumps | awk, perl-style regex, lua |

## The language matrix

Five languages, one discipline. Pick by *what's already on the box and what the job
smells like* — see [docs/taxonomy.md](docs/taxonomy.md) for the full reasoning.

- **bash** — default for process orchestration. Under ~100 lines, everything is a pipe.
- **zsh** — interactive ergonomics. Scripts stay bash-compatible; zsh tricks live in `.zshrc`.
- **python** — the escape hatch. Data structures, JSON, HTTP, anything past a screenful.
- **powershell** — Windows-native work, and genuinely good object pipelines anywhere.
- **lua** — embedded contexts: nginx, redis, neovim, wireshark, config-time transforms.

## Status

Five drills, thirteen solutions, all five families. `make check` runs the lot;
`make lint` syntax-checks every solution and validates the skill frontmatter.

| drill | family | languages | timebox |
| --- | --- | --- | --- |
| [001-csv-rollup](drills/001-csv-rollup) | data-wrangling | bash, python, lua | 4 min |
| [002-log-triage](drills/002-log-triage) | text-munging | bash, python, lua | 3 min |
| [003-http-probe](drills/003-http-probe) | api-probing | bash, python, pwsh | 3 min |
| [004-scrape-table](drills/004-scrape-table) | web-scraping | python, lua | 5 min |
| [005-dir-hygiene](drills/005-dir-hygiene) | file-hygiene | bash, python | 5 min |

Five matching [skills](skills/) carry the judgement each drill tests. The backlog in
[docs/taxonomy.md](docs/taxonomy.md#backlog) lists what comes next — process-glue,
polling, sqlite, encoding rescue, GNU-vs-BSD.

Contributing rules — including the no-abstraction rule — are in [AGENTS.md](AGENTS.md).

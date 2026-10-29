# scriptdeck

A training deck for **scripting** — the fast, dirty, in-between layer of programming.

Not systems work. Not low-level. Not web development. The work you do when you need an
answer in ten minutes: filter this data, probe that API, scrape the page, clean up the
directory, resort the files, then throw the script away.

```
scriptdeck/
├── docs/          what scripting is (and what it is not)
├── skills/        Agent Skills (SKILL.md) packs — loadable know-how
├── drills/        executable exercises: prompt + fixtures + verifier + solutions
└── harness/       runner and calibration gate
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
python3 harness/run.py run 001-csv-rollup --lang py
python3 harness/run.py run all --timeout 30
make calibrate ID=001-csv-rollup
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

A solution reads `<work>/in/`, writes `<work>/out/`, and exits non-zero on
failure. The harness maps its file extension to an interpreter and runs it in a
scratch directory. Some drills also generate fixture files, run a local mock
server, or probe a service started by the solution.

The **timebox** is part of the spec, not decoration. A drill that takes longer than its
timebox to solve is a signal you reached for the wrong tool or the wrong approach.
The runner's timeout is a separate execution limit.

The [runtime contract](docs/drill-spec.md) defines execution. The
[authoring and admission contract](docs/authoring-contract.md) defines what a
learner must see and what evidence is needed before a drill can be reused for
training or evaluation. Calibration runs the reference solutions and a
plausible wrong candidate against the same verifier, then records source hashes.
It establishes a local verifier result, not model competence.

## The seven families

| family | the job | typical tools |
| --- | --- | --- |
| `data-wrangling` | filter, join, aggregate, reshape | awk, jq, python, lua |
| `api-probing` | hit it, page it, retry it, time it | curl + jq, urllib, Invoke-RestMethod |
| `web-scraping` | pull structure out of markup that isn't yours | python html.parser, sed/awk, lua gsub |
| `file-hygiene` | triage, rename, dedupe, resort | bash, powershell, python |
| `text-munging` | extract, normalize, summarize logs & dumps | awk, perl-style regex, lua |
| `system-recon` | inspect host state and report bounded findings | shell, python, OS tools |
| `network-recon` | inspect network configuration and local protocol evidence | shell, python, curl |

## The language matrix

Five languages, one discipline. Pick by *what's already on the box and what the job
smells like* — see [docs/taxonomy.md](docs/taxonomy.md) for the full reasoning.

- **bash** — default for process orchestration. Under ~100 lines, everything is a pipe.
- **zsh** — interactive ergonomics. Scripts stay bash-compatible; zsh tricks live in `.zshrc`.
- **python** — the escape hatch. Data structures, JSON, HTTP, anything past a screenful.
- **powershell** — Windows-native work, and genuinely good object pipelines anywhere.
- **lua** — embedded contexts: nginx, redis, neovim, wireshark, config-time transforms.

## Status

The deck has expanded to more than 100 drills across seven families, including
data, files, operations, system and network reconnaissance, and agent workflow
tasks. `make list` is the current inventory. `make check` runs every available
solution against its drill; `make lint` checks syntax and skill frontmatter.
Those checks do not establish that a verifier rejects plausible wrong answers.
`make calibrate ID=001-csv-rollup` demonstrates that stronger gate on one
drill. Other drills remain to be calibrated before any farm admission claim.

The [skills](skills/) carry reusable judgment; the drills provide executable
practice. The [documentation index](docs/README.md) separates the live
contracts from the older taxonomy and manifesto.

Contributing rules — including the no-abstraction rule — are in [AGENTS.md](AGENTS.md).

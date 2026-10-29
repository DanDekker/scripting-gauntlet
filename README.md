# scripting-gauntlet

**Write the script. Get the answer. Prove it.**

A first-party training deck for the work between bigger builds: messy data,
awkward APIs, file cleanup, logs, host state, and network evidence. The script
can be disposable. The answer has to be right.

## Languages used

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/languages-dark.svg">
  <img src="assets/languages-light.svg" alt="Bash, Python, PowerShell, and Lua logos" width="640">
</picture>

The committed solutions use Bash, Python, PowerShell, and Lua. The harness uses
only the Python 3.11+ standard library.

## Run

```sh
make list
python3 harness/run.py run 001-csv-rollup --lang py
make check
make calibrate ID=001-csv-rollup
```

`make check` needs the interpreters used by the selected solutions. For a
single language, use `python3 harness/run.py run all --lang py`.

## The drill contract

Each drill has a task prompt, fixtures, an independent verifier, and at least
one reference solution. The runner copies the input into a fresh work
directory, exposes `$IN`, `$OUT`, and `$WORK`, then checks the answer's
behavior. A calibrated drill also has a plausible wrong solution that the
verifier must reject for the intended reason.

| Part | Job |
| --- | --- |
| `PROMPT.md` | The learner-visible task and output contract |
| `drill.toml` | Stable ID, family, difficulty, timebox, and taught skills |
| `fixtures/` | Messy but reproducible input |
| `verify.py` | Independent checks on the result |
| `solutions/` | Known-good implementations |
| `controls/` | Semantic negatives and their expected rejection |

The seven families are data wrangling, API probing, web scraping, file hygiene,
text munging, system reconnaissance, and network reconnaissance. `make list`
is the current inventory.

Start with [CSV rollup](drills/001-csv-rollup), [HTTP probing](drills/003-http-probe),
or [agent permission boundaries](drills/145-agent-permission-boundary).

[Runtime contract](docs/drill-spec.md) ·
[Authoring and admission](docs/authoring-contract.md) ·
[Documentation map](docs/README.md)

Reference calibration is local evidence. It does not by itself prove that a
model learned the task or that a dataset was admitted to a training farm.

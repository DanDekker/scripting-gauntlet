# AGENTS.md — working in scriptdeck

This repo trains **scripting**: fast, disposable, correct-for-now programs that answer a
question about messy data.

## The standard

1. **Correct beats clean.** A drill solution passes when its output is right. No tests,
   no classes, no config layer, no CLI framework.
2. **Small beats general.** Solve *this* fixture. Hardcoding a fixture's quirks is a
   legitimate scripting move — note it in `PROMPT.md` if you do.
3. **Loud beats silent.** On bad input, print what broke and exit non-zero. Never
   swallow an error to keep the pipeline alive.
4. **The timebox is real.** If a solution needs more than its `timebox` to write, the
   approach is wrong. Rethink, don't grind.

## Adding a drill

```bash
python3 harness/run.py new 007-my-drill   # scaffolds the directory
make check                                # must pass before you commit
```

Every drill needs, at minimum:

- `drill.yaml` with `id`, `family`, `title`, `difficulty` (1–5), `timebox` (seconds), `teaches`
- `PROMPT.md` stating the output contract exactly — inputs, output paths, sorting, formats
- `fixtures/` with input that is *messy in a realistic way* (blank rows, dupes, bad
  encoding, trailing whitespace, mixed case) and a note in `PROMPT.md` on which messes matter
- `verify.py` implementing `verify(io) -> list[str]` (empty list = pass). Assert semantics:
  parsed values, row sets, counts — never a raw byte diff
- at least one solution in `solutions/`, ideally a second language that makes a
  different trade-off

## Adding a skill

Skills follow the [Agent Skills spec](https://agentskills.io/specification): a directory
with `SKILL.md`, YAML frontmatter (`name` must equal the directory name, lowercase and
hyphenated; `description` says what it does *and* when to use it), optional
`references/` and `scripts/`. Keep `SKILL.md` under 500 lines and push detail into
`references/`.

A skill is *judgement*; a drill is *proof*. If you write a heuristic in a SKILL.md, there
should eventually be a drill that fails without it.

## Committing

Small, incremental, imperative-mood commits. One logical change each:
`harness: add mock-server support`, `drill: 004 scrape-table across bash/python/lua`.
Run `make check` before any commit that touches `drills/` or `harness/`.

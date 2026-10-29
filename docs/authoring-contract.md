# Drill authoring and admission

scripting-gauntlet trains short-lived scripting decisions. Its drills can inform Otto or a
Weaver curriculum, but passing a local solution is only local evidence. A drill is
not a model training sample, a held-out evaluation, or proof of learned skill.

## Learner contract

Write `PROMPT.md` before the reference solution. It must state everything the
solver needs to know:

1. **Objective:** the concrete question and observable result.
2. **Inputs:** file names, schemas, encoding, ordering, missing values, duplicates,
   and relevant malformed cases.
3. **Outputs:** exact paths, formats, sorting, comparison semantics, and exit
   behavior. Say when exact bytes matter.
4. **Constraints:** available runtimes and tools, timebox, allowed side effects,
   offline assumptions, and any portability requirement.
5. **Completion:** independently checkable predicates, tie breaks, tolerances,
   and failure conditions.
6. **Evidence access:** files and observations the solver can see. Keep controls
   and private acceptance data outside the learner's input.

The prompt and verifier must agree. A hidden convention cannot decide the grade.
When a requirement changes materially, revise the prompt, verifier, and controls
together, then recalibrate.

## Author packet

`drill.toml` holds the stable ID, family, title, difficulty, timebox, and taught
skills. The drill directory holds the prompt, fixtures, verifier, and at least
one reference solution. Record the source or synthetic origin of fixtures in
`PROMPT.md`; pin versions and dates for external facts that may change.

For admission beyond a draft, add `controls/manifest.toml` with `version = 1`,
a stable `lineage` group, `fixture_origin`, and one or more executable semantic
negatives. Each `[[negative]]` declares:

- `path`: a candidate under `controls/`;
- `defect`: the plausible mistake it makes;
- `expect`: a diagnostic substring from `verify.py` that proves the intended
  rule rejected it.

A syntax error, non-zero exit, timeout, missing interpreter, or failed setup
does not count as a semantic negative. The negative must reach the verifier.
Where the prompt permits multiple algorithms or output layouts, check a second
legitimate solution as well. Keep the verifier independent of the candidate:
it must check the promised result, not call the candidate or trust a success bit.

## Evidence stages

| Stage | Required evidence |
| --- | --- |
| authored | Complete learner contract, fixtures, independent verifier, reference, semantic control, and source lineage. |
| reference-calibrated | Current reference solutions pass and semantic controls fail at the intended verifier rule, with source hashes and recorded results. |
| capture-verified | A real agent attempt saw the stated inputs, produced the deliverable, and passed independent verification with a recorded tool trace. |
| dataset-verified | Exported examples have pinned source snapshots, lineage-aware splits, deduplication, and exact reconstruction checks. |
| consumer-verified | The intended trainer or runtime ingested the exact serialized data and preserved the supervision contract. |
| checkpoint-evaluated | A named checkpoint improved against a predeclared held-out baseline under recorded conditions. |

The local calibration command can establish **reference-calibrated** only. It
does not sample teachers, build a dataset, or test Otto. Those stages need
separate Weaver and Otto evidence.

The local runner isolates output files, but it is not a security sandbox:
executed solutions can read the checkout. A capture intended for training or
held-out evaluation must materialize a learner workspace that excludes
`solutions/`, `controls/`, `verify.py`, and private acceptance data.

Run a calibrated drill and retain a fresh JSON report with the contract:

```sh
python3 harness/calibrate.py 001-csv-rollup --out docs/evidence/001-csv-rollup.json
```

The report hashes the prompt, metadata, verifier, fixtures, reference solutions,
and controls. A later edit changes those hashes and makes the earlier result
historical evidence rather than a current pass.

## Promotion toward Weaver or Otto

Before exporting a drill into a farm, pin the task and source revisions, define
the exact learner-visible packet, keep controls and references out of that packet,
and assign a lineage group so related variants cannot straddle training and
held-out evaluation. Record the actual execution environment, tools, limits,
attempts, and verifier results. Match the consuming model's real tokenization
and data format; a Markdown prompt or local calibration report is not a native
training artifact.

For the upstream standards, see Weaver's `TASK_AUTHORING_CONTRACT.md` and
`scripts/FARMING.md`, plus Otto's `docs/design/OTTO_CODE_CLI.md`. Their
project-specific model, engine, and farm rules remain owned by those projects.

# scripting-gauntlet documentation

Start with the live contracts:

1. [Drill spec](drill-spec.md) — metadata, file layout, runtime environment,
   interpreters, and verifier interface.
2. [Authoring and admission](authoring-contract.md) — learner-visible task
   requirements, independent controls, source lineage, and evidence stages.
3. [Harness guide](../harness/README.md) — commands for running drills.

The [taxonomy](taxonomy.md) explains the seven scripting families and language
choices. The [manifesto](manifesto.md) states the deck's scope and style; it is
not an executable contract.

`harness/run.py` is the implementation of the local execution contract.
`harness/calibrate.py` records reference and semantic-negative evidence for
drills that have controls. If documentation and the runner disagree, repair
the mismatch before treating a drill as calibrated.

Calibration reports with source hashes and negative-control results:

- [CSV rollup](evidence/001-csv-rollup.json)
- Data cleaning: [number parsing](evidence/019-number-parsing.json),
  [date parsing](evidence/020-date-parsing.json),
  [Unicode normalization](evidence/021-unicode-normalize.json), and
  [type inference](evidence/022-type-inference.json)
- Operations: [percent of group](evidence/057-percent-of-group.json) and
  [outer join](evidence/058-outer-join.json)
- [macOS plist audit](evidence/149-macos-plist-audit.json)

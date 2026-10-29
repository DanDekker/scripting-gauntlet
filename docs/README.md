# scriptdeck documentation

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

The [001-csv-rollup calibration](evidence/001-csv-rollup.json) is the first
durable reference and negative-control record.

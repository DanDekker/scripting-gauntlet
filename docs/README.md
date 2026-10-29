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
- Lua: [pattern fields](evidence/150-lua-pattern-fields.json),
  [exact decimals](evidence/151-lua-exact-decimals.json),
  [UTF-8 characters](evidence/152-lua-utf8-chars.json),
  [sort ties](evidence/153-lua-sort-ties.json),
  [error levels](evidence/154-lua-error-level.json),
  [JSON writer](evidence/155-lua-json-writer.json),
  [sparse arrays](evidence/156-lua-sparse-array.json),
  [needle search](evidence/157-lua-needle-haystack.json),
  [plugin order](evidence/158-lua-plugin-order.json),
  [disk scan](evidence/159-lua-disk-scan.json), and
  [file hunt](evidence/160-lua-file-hunt.json)
- Perl: [split limits](evidence/161-perl-split-limits.json),
  [numification](evidence/162-perl-numify.json),
  [literal matching](evidence/163-perl-literal-match.json),
  [hash order](evidence/164-perl-hash-order.json), and
  [epoch conversion](evidence/165-perl-timegm.json)
- Ruby: [integer division](evidence/166-ruby-integer-division.json),
  [hash identity](evidence/167-ruby-hash-identity.json),
  [truthiness](evidence/168-ruby-truthiness.json),
  [mixed sorting](evidence/169-ruby-sort-mixed.json), and
  [float formatting](evidence/170-ruby-float-format.json)
- Lua, advanced: [integer subtype](evidence/171-lua-integer-subtype.json),
  [coroutine pipeline](evidence/172-lua-coroutine-pipeline.json), and
  [load sandbox](evidence/173-lua-load-sandbox.json)
- Perl, advanced: [binary unpack](evidence/174-perl-unpack-binary.json) and
  [version sorting](evidence/175-perl-version-sort.json)
- PowerShell: [case-folded grouping](evidence/176-ps1-group-folding.json) and
  [decimal money](evidence/177-ps1-decimal-money.json)
- Deeper, Lua: [number printing](evidence/178-lua-number-printing.json) and
  [metatable layers](evidence/179-lua-metatable-layers.json)
- Deeper, Perl: [substitution eval](evidence/180-perl-substitution-eval.json) and
  [substr/index offsets](evidence/181-perl-substr-index.json)
- Deeper, Ruby: [hash defaults](evidence/182-ruby-hash-default.json) and
  [encoding scrub](evidence/183-ruby-encoding-scrub.json)
- Deeper, PowerShell: [JSON depth](evidence/184-ps1-json-depth.json) and
  [datetime parsing](evidence/185-ps1-datetime.json)
- Advanced scripting: [Bash nameref dispatch](evidence/186-bash-nameref-dispatch.json),
  [Lua binary pack](evidence/187-lua-binary-pack.json),
  [Perl context dispatch](evidence/188-perl-context-dispatch.json),
  [Ruby lazy pipeline](evidence/189-ruby-lazy-pipeline.json), and
  [PowerShell exitcode trap](evidence/190-ps1-exitcode-trap.json)

# scripting-gauntlet documentation

Start with the live contracts:

1. [Drill spec](drill-spec.md) — metadata, file layout, runtime environment,
   interpreters, and verifier interface.
2. [Authoring and admission](authoring-contract.md) — learner-visible task
   requirements, independent controls, source lineage, and evidence stages.
3. [Harness guide](../harness/README.md) — commands for running drills.

The current language-depth expansions are [PowerShell 240-247](../drills/ps/240-ps1-split-regex),
[JXA 248-254](../drills/jxa/248-jxa-json-bridge), and
[Tcl 255-262](../drills/tcl/255-tcl-split-fields). Each drill has a reference solution,
a portable twin where useful, and a calibration report under evidence/.

## Recent language-depth evidence

- PowerShell: [240 regex splitting](evidence/240-ps1-split-regex.json),
  [241 JSON presence](evidence/241-ps1-json-presence.json),
  [242 TryParse](evidence/242-ps1-tryparse.json),
  [243 quoted CSV](evidence/243-ps1-csv-quoted.json),
  [244 literal patterns](evidence/244-ps1-literal-pattern.json),
  [245 UTF-16](evidence/245-ps1-utf16.json),
  [246 LiteralPath](evidence/246-ps1-literal-path.json), and
  [247 object export](evidence/247-ps1-format-object.json)
- JXA: [248 JSON bridge](evidence/248-jxa-json-bridge.json),
  [249 Unicode file I/O](evidence/249-jxa-file-io.json),
  [250 path inventory](evidence/250-jxa-path-inventory.json),
  [251 timezone parsing](evidence/251-jxa-date-timezone.json),
  [252 plist writing](evidence/252-jxa-plist-write.json),
  [253 NSError handling](evidence/253-jxa-objc-errors.json), and
  [254 URL components](evidence/254-jxa-url-components.json)
- Tcl: [255 split fields](evidence/255-tcl-split-fields.json),
  [256 dict presence](evidence/256-tcl-dict-presence.json),
  [257 regexp records](evidence/257-tcl-regexp-records.json),
  [258 literal files](evidence/258-tcl-file-literal.json),
  [259 safe subst](evidence/259-tcl-safe-subst.json),
  [260 catch and expr](evidence/260-tcl-catch-expr.json),
  [261 deterministic dict sort](evidence/261-tcl-dict-sort.json), and
  [262 list quoting](evidence/262-tcl-list-quoting.json)

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
- Language mastery II: [Bash assoc presence](evidence/191-bash-assoc-presence.json),
  [Lua env sandbox](evidence/192-lua-env-sandbox.json),
  [Perl regex lookaround](evidence/193-perl-regex-lookaround.json),
  [Ruby keyword arguments](evidence/194-ruby-keyword-arguments.json), and
  [PowerShell pipeline unrolling](evidence/195-ps1-pipeline-unrolling.json)
- Milestone 200 language depth: [Bash heredoc expansion](evidence/196-bash-heredoc-expansion.json),
  [Lua coroutine filter](evidence/197-lua-coroutine-filter.json),
  [Perl state variables](evidence/198-perl-state-variables.json),
  [Ruby Forwardable delegation](evidence/199-ruby-forwardable-delegation.json), and
  [PowerShell regex groups](evidence/200-ps1-regex-groups.json)

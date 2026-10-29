# harness

`run.py` executes drills; `calibrate.py` checks references against semantic
negatives. Both use Python 3.11+ and the standard library.

```bash
python3 harness/run.py list
python3 harness/run.py run 001-csv-rollup --lang py
python3 harness/run.py run all -v
python3 harness/run.py new 007-my-drill --family text-munging --title "..."
python3 harness/calibrate.py 001-csv-rollup --out docs/evidence/001-csv-rollup.json
```

Exit code is 0 only if everything selected passed, so `make check` is CI-able.
The browser DOM reference needs Node and `npm ci --ignore-scripts`; the JXA
reference runs on macOS and is reported as skipped elsewhere.
Calibration returns 0 only if every reference passes and every declared
negative is rejected by its intended verifier rule. See the
[runtime contract](../docs/drill-spec.md) and
[authoring contract](../docs/authoring-contract.md).

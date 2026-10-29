# harness

One file: `run.py`. Stdlib only, Python 3.11+ (uses `tomllib`).

```bash
python3 harness/run.py list
python3 harness/run.py run 001-csv-rollup --lang python
python3 harness/run.py run all -v
python3 harness/run.py new 007-my-drill --family text-munging --title "..."
```

Exit code is 0 only if everything selected passed, so `make check` is CI-able.
See [../docs/drill-spec.md](../docs/drill-spec.md) for the runtime contract.

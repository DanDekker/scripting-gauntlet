# 085-batch-install

> "Two release batches. One is good, one has a typo in a key. Install the good one
> completely, reject the bad one completely, and never leave me with half a deploy."

## Task

`in/target/` is the current config directory. `in/batch-a/` and `in/batch-b/` hold staged
files. Install each batch, in order, into `out/target/`.

## Rules

1. A batch is **valid** when every file in it contains only `key=value` lines, where the
   key matches `^[a-z_][a-z0-9_]*=`; blank lines and `#` comments are allowed.
2. Validate the whole batch first. If any file is invalid, install **nothing** from it and
   append exactly one line `rejected <batch>/<file>:<line>` to `out/reject.log`, naming the
   first offending file and line. A rejection is a normal outcome, not an error.
3. Installing a batch copies each staged file into `out/target/` via a temp file in that
   directory followed by a rename. Files already in the target that the batch does not
   mention stay untouched.
4. Before installing, back up the target. If a copy or rename fails part-way, restore the
   backup and exit non-zero.
5. Process `batch-a`, then `batch-b`.

## Output

- `out/target/` - the final config directory.
- `out/reject.log` - one line per rejected batch.
- `out/summary.json` - exactly four integers: `applied_files`, `kept_files` (target files
  no batch touched), `total_files` (files in the final target), `rejected_batches`.

## Messes to expect

- one batch that updates two files and adds a new one
- one batch whose only new file has an uppercase key
- a target file that no batch mentions

## Timebox

5 minutes. Validate, back up, rename each file, then delete the backup.

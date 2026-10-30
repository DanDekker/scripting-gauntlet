# 238-perl-du-quota

> "Our nightly disk audit generates human-readable `du -h` summaries across user directories.
> Several users are blowing past their assigned quotas and filling shared mountpoints.
> We need a script to convert the human-readable sizes to exact byte counts, cross-reference
> against a quota schedule, and produce an over-quota alert report."

## Input

- `in/usage.txt` — disk usage lines formatted as `<size>\t<path>`:
  - Sizes contain an integer or decimal number followed by an optional unit suffix:
    `B` (bytes), `K` (kibibytes, 1024 B), `M` (mebibytes, 1024² B), `G` (gibibytes, 1024³ B),
    `T` (tebibytes, 1024⁴ B).
    Suffixes may be uppercase or lowercase (`k`, `m`, `g`, `t`, `b`).
    If no suffix is present or suffix is `B`/`b`, multiplier is 1.
  - Path is the directory path (e.g. `/home/bob`).
- `in/quotas.tsv` — tab-separated quota table with header `path\tquota`:
  - `path`: directory path or the literal keyword `DEFAULT`.
  - `quota`: human-readable size limit (same format as usage).
  - Any directory from `in/usage.txt` not explicitly present in `in/quotas.tsv` uses the
    `DEFAULT` quota entry.

Empty lines and lines starting with `#` are ignored in both files.

## Rules

1. Convert human-readable size strings to exact byte counts:
   - Base 1024 multiplier: `B`=1, `K`=1024, `M`=1,048,576, `G`=1,073,741,824, `T`=1,099,511,627,776.
   - Suffix matching is case-insensitive.
   - Bytes = `int($value * $multiplier + 0.5)`.
2. Evaluate each directory against its quota:
   - If `usage_bytes > quota_bytes`, the directory is **over quota**.
   - `overage_bytes = usage_bytes - quota_bytes`.
   - `pct_used = sprintf("%.1f", (usage_bytes / quota_bytes) * 100)`.
3. **`out/alerts.tsv`** — tab-separated values (`\t`) for over-quota directories:
   - Header: `path\tusage_bytes\tquota_bytes\toverage_bytes\tpct_used`
   - Sorted by `overage_bytes` **descending** numerically (`<=>`); ties broken by `path` **ascending** in ASCII order (`cmp`).
4. **`out/summary.json`** — compact JSON object with keys:
   - `total_checked`: total number of valid directories inspected from `in/usage.txt`.
   - `over_quota_count`: number of directories exceeding their quota (rows in `out/alerts.tsv`).
   - `total_overage_bytes`: sum of `overage_bytes` across all over-quota directories.
   - `top_offender`: `path` of the directory with the highest `overage_bytes` (tie broken by `path` ascending). If no directories are over quota, empty string `""`.

## Messes to expect

- Mixed-case unit suffixes: e.g. `800m`, `1.5G`, `512K`, `12000B`.
- Directories with no explicit quota rule in `in/quotas.tsv` must resolve to the `DEFAULT` quota.
- Header row in `in/quotas.tsv` must be skipped.

## Timebox

Five minutes.


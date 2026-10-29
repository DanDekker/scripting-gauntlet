# 089-semver-sort

> "Given a messy list of release tag strings from git, filter out invalid versions,
> sort the valid versions in standard SemVer 2.0.0 order (oldest to newest), and identify
> the latest stable release and latest prerelease."

## Input

`in/tags.txt` — one raw version string per line.

Messy characteristics:
- leading/trailing whitespace and empty lines
- optional leading `v` or `V` (e.g. `v1.2.3`, `V2.0.0`)
- build metadata tags with `+` (e.g. `1.0.0+20130313144700`) which must be retained in output, but ignored for precedence ordering
- prerelease tags with `-` (e.g. `1.0.0-alpha.1`, `1.0.0-beta`, `1.0.0-rc.2`)
- invalid non-semver lines (e.g. `latest`, `2024.10.1`, `v1.2`, `1.0.0.4`, `alpha-release`) which must be skipped

## SemVer 2.0.0 Precedence Rules

1. Format: `MAJOR.MINOR.PATCH` with optional `-PRERELEASE` and optional `+BUILD`.
2. A normal version (without prerelease) has higher precedence than the same version with a prerelease (e.g. `1.0.0` > `1.0.0-rc.1`).
3. Prerelease parts are dot-separated identifiers:
   - numeric identifiers are compared numerically (`alpha.2` < `alpha.10`).
   - non-numeric identifiers are compared ASCII lexicographically (`alpha` < `beta`).
   - numeric identifier has lower precedence than non-numeric identifier (`1` < `alpha`).
   - a larger set of pre-release fields has a higher precedence than a smaller set, if all of the preceding identifiers are equal (`1.0.0-alpha` < `1.0.0-alpha.1`).
4. Build metadata does not affect precedence. When versions have equal precedence, preserve their original relative input order (stable sort).

## Output

1. **`out/sorted.txt`** — the valid original tag strings (whitespace-trimmed), sorted in ascending SemVer order (oldest first).
2. **`out/summary.json`** — JSON object with keys:
   - `total_lines`: integer count of non-empty lines in input
   - `valid_count`: integer count of valid SemVer tags
   - `latest_stable`: string tag of the newest valid release without prerelease (or `null` if none)
   - `latest_overall`: string tag of the newest valid release overall

# 110-license-scan

> "Legal wants to know whether we can ship this dependency list. Match every dependency
> against the licence policy — and be careful: a licence the policy has never heard of is
> not the same thing as a licence we are not allowed to use."

## Input

- `in/deps.txt` — one dependency per line: `name version licence`, e.g.
  `requests 2.31.0 MIT`.
- `in/policy.csv` — header `licence,allowed`; `allowed` is `yes` or `no`. The policy does
  **not** list every licence.

Messes in the fixtures: trailing whitespace, a line with only a name, a line with five
fields, a blank line, a duplicate dependency (same name, different version), an identical
repeat of a name+version, a lower-case licence (`mit`), an upper-case licence name
(`Django`), a licence with a trailing `License` suffix in the dependency list
(`Apache-2.0 License`, `BSD-3-Clause License`), a policy entry that carries the same
`License` suffix, and two licences the policy does not mention at all.

## Rules

1. **Normalise a licence**: trim it, lowercase it, and strip a trailing `license` (with the
   whitespace before it), then trim again. `Apache-2.0 License` → `apache-2.0`,
   `mit` → `mit`, `agpl-3.0` → `agpl-3.0`. The policy's licences are normalised the same
   way before they are looked up, so the policy's `Apache-2.0 License` row answers for
   `apache-2.0`.
2. **A dependency line is valid** when it splits into exactly three whitespace-separated
   fields — with one documented fold: four fields whose last field is `license`
   (case-insensitive) are valid too, and that word is folded back into the licence field
   (`click 8.1.7 BSD-3-Clause License` is a valid dependency whose licence is
   `BSD-3-Clause License`). Every other line — a blank line, a line with one field, a line
   with five — is skipped and counted as skipped, never repaired.
3. **Status** of a valid dependency, from the normalised licence:
   - `allowed` — the licence is in the policy with `allowed` = `yes`
   - `denied` — the licence is in the policy with `allowed` = `no`
   - `unknown` — the licence is not in the policy at all
4. **Conflicts**: two valid dependency lines with the same name but different version
   strings are in conflict. An identical repeat (same name *and* same version) is not a
   conflict. `conflicts` counts **names**, not lines.
5. A denied licence is the blocker, an unknown licence is a warning. Both are reported as
   their own status; neither is silently folded into the other.

## Output

Write exactly these files to `$OUT`:

1. **`out/deps.csv`** — header `name,version,licence,status`. One row per **valid**
   dependency line — a dependency that repeats appears once per line it was written on.
   Sorted by `name` ascending (byte order), then `version` ascending (byte order: `2.28.2`
   sorts before `2.31.0`, and this is a string comparison, not semantic versioning); rows
   that tie on both keep their original file order. `licence` is the **normalised** licence,
   never the string as written. `status` is exactly `allowed`, `denied` or `unknown`.
2. **`out/summary.json`** — an object with exactly these keys:
   - `deps` — valid dependency lines (int)
   - `skipped` — malformed lines, blank lines included (int)
   - `allowed` — valid dependencies whose status is `allowed` (int)
   - `denied` — those with status `denied` (int)
   - `unknown` — those with status `unknown` (int)
   - `conflicts` — number of names in conflict (int)

## Messes to expect

- `requests` appears at `2.31.0` twice and at `2.28.2` once: three rows, and **one**
  conflict — the identical repeat does not invent a second one.
- `numpy 1.26.4 mit` is `allowed`, because the licence is normalised before the lookup.
- `pandas 2.2.0 PSF-2.0` and `cryptography 42.0.5 OpenSSL` are `unknown`, not `denied` —
  the policy never mentions them, and only `GPL-3.0`/`AGPL-3.0` are listed as `no`.
- `Django` sorts before the lower-case names (byte order), and its licence is `mit` in the
  output because licences are normalised even when they were already upper case.
- `click 8.1.7 BSD-3-Clause License` is four fields, so the trailing `License` word is
  folded into the licence field before normalisation; the line is valid and
  `BSD-3-Clause License` normalises to `bsd-3-clause`.
- `urllib3` (one field), `too many fields here indeed` (five fields) and the blank line are
  skipped: three skipped lines, twelve dependencies.

## Timebox

Four minutes. If you are past that, the approach is wrong.

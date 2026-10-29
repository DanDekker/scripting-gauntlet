# 115-dep-resolve

> "`pip freeze` and `requirements.txt` have drifted apart again. Tell me, per declared
> requirement, whether the installed world satisfies it — and which installed packages
> nobody asked for."

## Input

- `in/requirements.txt` — one requirement per line, e.g. `requests>=2.28`,
  `flask==2.0.1`, `urllib3~=1.26`, `numpy`, `django>=4,<5`, `pkg[extra]>=1.0`,
  `foo ; python_version < "3.10"`.
- `in/installed.txt` — one installed package per line: `name version`, whitespace-separated,
  e.g. `requests 2.31.0`.

The requirement file is messy in realistic ways: a blank line, a `#` comment line, a
requirement followed by an inline `#` comment, a line with trailing spaces, a requirement
naming a package that is not installed, a requirement the installed version does not
satisfy, an exact pin that matches, an unpinned requirement, a package required twice, an
environment marker, an extras block, a sole `!=` specifier, and a `.*` wildcard version.

## Rules

1. **Which lines are requirements.** Trim the line, then:
   - a blank line is skipped;
   - a line starting with `#` is skipped;
   - a line containing `;` anywhere is skipped entirely (an environment marker — even if it
     would otherwise parse);
   - an inline comment is anything from the first `#` onward: cut it off, then trim again.
2. **Parsing a requirement.** `name`, then an optional `[extras]` block (ignored — the name
   is the part before it), then an optional specifier set. A name is one or more characters
   from `A-Z a-z 0-9 _ . -`. The rest of the line, trimmed, is the `required` text: for
   `django>=4,<5` it is `>=4,<5`; for `numpy` it is empty.
3. **Comparison.** Versions are compared component-wise as integers split on `.`, with the
   shorter one padded with zeros (`1.16` equals `1.16.0`). A version may end in `.*`, which
   means "any version with this prefix" — `==2.*` matches `2.6`; it is only meaningful on
   `==`/`!=`.
4. **Operators.** A specifier set is a comma-separated list and **every** specifier must
   match:
   - `==` equal, `!=` not equal (with `.*`: prefix-equal / prefix-different);
   - `>=`, `>`, `<=`, `<` compare component-wise;
   - `~=` is compatible-release: the installed version must be `>=` the given version
     **and** its components must match the given version's components *minus the last
     one*. So `~=1.2.3` keeps the prefix `1.2`: `1.2.9` matches, `1.3.0` does not.
     `~=1.26` keeps the prefix `1` and additionally requires `>=1.26`, so `1.25.11` is
     `conflicted`.
5. **Status**, per considered requirement:
   - `missing` — the package is not in `installed.txt`;
   - `conflicted` — it is installed but at least one specifier does not match;
   - `satisfied` — installed and every specifier matches (a requirement with no specifier
     set is satisfied by any installed version).
6. **Duplicates.** A package named by more than one line is considered **once**, from its
   **first** occurrence; later lines for the same name are ignored completely.
7. **Extras.** An installed package whose name is not a considered requirement is "extra".

## Output

Write exactly these files to `$OUT`:

1. **`out/deps.csv`** — header `name,status,installed,required`. One row per considered
   requirement, sorted by `name` ascending (byte order).
   - `status` — exactly `satisfied`, `conflicted` or `missing`.
   - `installed` — the installed version string, or empty when missing.
   - `required` — the specifier text, or empty when there was none.
   - CSV quoting: a field containing a comma (e.g. `>=4,<5`) is wrapped in double quotes per
     RFC 4180. Nothing else is quoted.
2. **`out/summary.json`** — an object with exactly these keys:
   - `requirements` — considered requirements (int)
   - `satisfied`, `conflicted`, `missing` — counts per status (int)
   - `extra` — installed packages no requirement names (int)
   - `extras` — the names of those packages, sorted ascending (list of strings)

## Messes to expect

- `foo ; python_version < "3.10"` is ignored, so `foo` never appears in `deps.csv`
- `pkg[extra]>=1.0` is the package `pkg` with specifier `>=1.0` — the extras block is not
  part of the name and does not appear in `required`
- `requests` appears twice; only `>=2.28` from the first line counts, so `==2.30.0` is dead
  text and `requests` is `satisfied` (not a conflict)
- `click>=8.0  # CLI deps` is `click` with specifier `>=8.0` after the comment is cut
- `django>=4,<5` with `3.2.0` installed is `conflicted`; `urllib3~=1.26` with `1.25.11` is
  also `conflicted`; `idna==2.*` with `2.6` is `satisfied`
- `six>=1.16` against `1.16` is `satisfied` — a missing component pads with zero
- `pyyaml!=6.0.0` against `5.4.1` is `satisfied`
- `orjson` is `missing`: no installed version, so `installed` is empty
- `other` and `pip` are installed but never required, so they land in `extras`

## Timebox

Five minutes. If you are past that, the approach is wrong.

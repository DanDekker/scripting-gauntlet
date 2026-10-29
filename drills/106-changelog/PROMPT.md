# 106-changelog

> "The release notes are being written by hand and they are wrong every time. Read the
> commit log and give me a changelog — grouped, ordered, and honest about the commits you
> could not place."

## Input

`in/commits.txt` — one commit subject per line, Conventional Commits form:

```
feat(parser): add csv support
fix: handle empty input
```

It is messy in realistic ways: a blank line, a line that is not a conventional commit at
all (`just some work`), a line whose type is capitalised (`Feat: wrong case`), a `feat` with
no scope, a `feat` with an empty scope `()`, a subject with trailing whitespace, and
`BREAKING CHANGE:` trailer lines that belong to the commit above them.

## Rules

1. **Trim first.** Strip trailing carriage returns and surrounding whitespace from every
   line. A line that is empty after trimming is skipped and counts nowhere.
2. **A trailer is not a commit.** A line starting with `BREAKING CHANGE:` marks the commit
   it follows and is never emitted or counted as a commit. The commit it marks is the
   closest commit line above it (blank lines do not detach it); if the line directly above it
   is not a commit line, the trailer marks nothing.
3. **Conventional form.** A line is a conventional commit when it matches
   `^<type>(\([^)]*\))?(!)?: <subject>$` where `<type>` is exactly one of `feat`, `fix`,
   `docs`, `refactor`, `perf`, `test`, `chore`, `build`, `ci` — lowercase, so `Feat:` is not
   conventional. A non-conventional line is **skipped**: it is counted in `skipped` and
   appears nowhere in the changelog. The subject is everything after the single `: `.
4. **Breaking.** A commit is breaking when it has a `!` immediately before the colon, or
   when a `BREAKING CHANGE:` trailer marks it.
5. **Internal types.** A commit whose type is `chore`, `build`, `ci` or `test` is internal:
   it is counted in `internal` and appears in **no** section — except `Breaking Changes`,
   which includes breaking internal commits.
6. **Sections**, in this order: `Features` (feat), `Bug Fixes` (fix), `Performance` (perf),
   `Refactoring` (refactor), `Documentation` (docs), `Breaking Changes`.
   A section with no entries is omitted entirely. Inside a section the entries are in
   commit order, not sorted.

## Output

Write exactly these files to `$OUT`:

1. **`out/changelog.md`** — for each non-empty section, a `## <Name>` line followed by one
   `- <subject>` line per commit. The `<subject>` is the text after `: `, so the scope and
   the `!` never appear in a bullet. Sections are separated by exactly one blank line and
   the file ends with a single newline after the last bullet. No title, no preamble.
2. **`out/summary.json`** — an object with exactly these keys, all ints:
   - `commits` — commit lines: every non-blank line except a `BREAKING CHANGE:` trailer, so
     `commits == conventional + skipped`
   - `conventional` — lines that matched the conventional form
   - `skipped` — non-blank, non-trailer lines that did not match
   - `internal` — conventional commits of an internal type
   - `breaking` — commits that are breaking (internal ones included)
   - `features` — commits of type `feat`
   - `fixes` — commits of type `fix`

## Messes to expect

- `just some work` and `Feat: wrong case` are skipped: `commits` counts them,
  `conventional` does not
- `refactor!: drop legacy api` is breaking from the `!`, subject `drop legacy api`
- `perf(cache): memoise lookups` is breaking because the next line is
  `BREAKING CHANGE: cache keys changed` — that trailer is not a commit
- `build: switch to esbuild` is internal *and* breaking, so it appears only under
  `Breaking Changes`, never under a `Build` heading
- `feat(): support windows paths` is conventional — the scope may be empty
- `fix(ui): repair tooltip` has trailing spaces that must not reach the bullet

## Timebox

Four minutes. If you are past that, the approach is wrong.

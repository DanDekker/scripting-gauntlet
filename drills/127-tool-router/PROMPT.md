# 127-tool-router

> "The agent gets a request in English and a catalogue of tools. Point it at the right tool —
> and when nothing fits, say so instead of grabbing the least-wrong hammer."

## Input

- `in/tools.json` — the catalogue:

```json
{"tools":[{"name":"search_code","keywords":["grep","search","find","locate"],"requires":["repo"]}]}
```

  Each tool has a `name` (string), `keywords` (list of strings) and `requires` (list of
  capability strings). A missing `requires` means an empty list.
- `in/requests.jsonl` — one JSON object per line:

```json
{"id":"r1","text":"find the definition of parse_config in the repo","context":["repo"]}
```

  `id` and `text` are strings, `context` is a list of capability strings the caller can
  actually use right now.

The request file is messy on purpose: blank lines, a line that is not valid JSON, a line that
is a JSON array, a record with no `id`, a record with no `text`, a record with no `context`
at all, an empty `text`, a whitespace-only `text`, two records that share an `id`, mixed case
in the text, and a keyword that only appears inside a longer word.

## Rules

1. **Skip junk.** A blank line, a line that is not valid JSON, a line that parses to something
   that is not an object, and an object whose `id` or `text` is missing or not a string are
   all skipped. A skipped line is not a request and counts nowhere. Every other object is an
   **accepted request**, in input order — including a repeated `id` (both are processed).
2. **Context.** The request's context is its `context` list; a missing or non-list `context`
   is the empty list.
3. **A keyword matches** when it occurs in the request's `text` **case-insensitively**:
   - a keyword made only of letters, digits and `_` matches as a **whole word**: the characters
     immediately before and after the match must not be letters, digits or `_`. So `test`
     matches `test` and `TEST` but not `contest`, `tests` or `pytest`.
   - a keyword that contains any other character (e.g. `c++`) matches as a plain **substring**,
     case-insensitively.
4. **A tool matches** when at least one of its keywords matches. Its `matched` count is how
   many of its keywords match — each keyword counts once, however often it appears.
5. **A tool is available** when every entry of its `requires` list appears in the request's
   context (string equality, case-sensitive). An empty `requires` list is always available.
6. **The chosen tool** is the available matching tool with the **highest** `matched` count;
   on a tie, the **alphabetically first** tool name (byte order). A tool that is unavailable is
   never chosen, even when it is the only tool that matches. A request with no available
   matching tool is **UNROUTED**: its tool is the empty string and `matched` is `0`.

## Output

Write exactly these files to `$OUT`:

1. **`out/routes.csv`** — header `id,tool,matched`. One row per **accepted** request, in input
   order. `tool` is the chosen tool name, or the empty string when the request is unrouted.
   `matched` is the chosen tool's matching-keyword count, `0` when unrouted. Ids contain no
   commas, so fields are written raw — an unrouted row has an empty middle field.
2. **`out/summary.json`** — an object with exactly these keys:
   - `requests` — accepted records (int)
   - `routed` — requests with a chosen tool (int)
   - `unrouted` — requests without one (int)
   - `by_tool` — object mapping each tool **that was actually chosen** to the number of
     requests routed to it; a tool never chosen does not appear, and the object is `{}` when
     nothing routed

## Messes to expect

- `who won the contest last year` is unrouted: `test` inside `contest` is not a whole word
- `run the ci pipeline and check pytest output` routes to `run_tests` with `matched` 2 (`ci`,
  `pytest` — `test` inside `pytest` does **not** count)
- `grep and find and locate the symbol` with context `["path"]` is unrouted: `search_code`
  matches three keywords but needs `repo`, and an unavailable tool never wins
- `read the source and grep for TODO` with context `["path"]` routes to `read_file`: the
  better-scoring tool is gated out
- `search the web for this error code` with an empty context routes to `web_search` with
  `matched` 2, because `web_search` requires nothing
- `search for the symbol in the repo` is a tie between `search_code` and `web_search` at
  `matched` 1: `search_code` wins alphabetically
- `OPEN the config file` matches `open` (case-insensitive); `the C++ build is broken` matches
  `c++` as a substring
- `open the README` with no `context` key at all has an empty context, so `read_file` is
  unavailable and the request is unrouted
- the invalid-JSON line, the array line, the no-`id` line and the no-`text` line are skipped,
  so `requests` is smaller than the number of non-blank lines
- the two `dup` records both appear, one row each

## Timebox

Five minutes. Parse, score, sort candidates, take the first.

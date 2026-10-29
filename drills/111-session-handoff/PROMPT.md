# 111-session-handoff

> "The session is out of context and another agent has to pick it up. Read this transcript
> and write the handoff note: what was asked last, what was actually touched, what is still
> broken — and how much of the work nobody ever got a result for."

## Input

`in/session.log` — a transcript of an agent session. Lines look like:

```
USER: please fix the failing parser test
TOOL read_file src/parser.py     (a tool call, no result of its own)
RESULT read_file: 214 lines
NOTE: the parser drops trailing whitespace
ERROR: TimeoutError after 30s
USER: also update the docs
```

Messes in the fixture: an indented line before anything else (a continuation with no
parent), blank lines, indented continuation lines — one with trailing whitespace — a tool
called twice, a tool that is called and never returns a result, a bare `TOOL` line with no
name, and a `RESULT` line with no colon.

## Rules

1. **A line that starts with whitespace is a continuation.** It is appended to the previous
   non-continuation line, separated by a single space, after its own leading and trailing
   whitespace is trimmed. A continuation of a continuation is appended the same way. A
   continuation before any line at all is ignored, and a continuation whose trimmed text is
   empty adds nothing.
2. **Classification happens after continuations are folded in**, and it is case-sensitive on
   the keyword:
   - `USER:` at the start of the trimmed line — a **request**; its text is the rest of the
     line, trimmed.
   - `TOOL` followed by whitespace — a **tool call**; the tool name is the first
     whitespace-separated token after `TOOL`. A bare `TOOL` with nothing after it is not a
     call.
   - `RESULT` followed by whitespace — a **tool result**; it must contain a colon, and the
     tool name is the text between `RESULT` and that first colon, trimmed. A `RESULT` line
     with no colon is not a result.
   - `NOTE:` at the start of the trimmed line — a **note**; its text is the rest, trimmed.
   - `ERROR:` at the start of the trimmed line — an **error**; its text is the rest, trimmed.
3. Every other line (blank lines, prose) is nothing and counts nowhere.

## Output

Write exactly one file to `$OUT`:

**`out/handoff.json`** — an object with exactly these keys:

- `request` — the text of the **last** request in the session; `""` if there is none
- `tools` — the distinct tool names called, in the order they were first called
- `results` — number of tool result lines (int)
- `notes` — every note text, in order (list of strings)
- `errors` — every error text, in order (list of strings)
- `calls` — number of tool call lines (int)
- `unresolved` — number of tool calls whose tool name has **no** result line anywhere in
  the session (int); a tool called twice with no result counts twice

## Messes to expect

- `user=` and prose lines are not requests; only a line whose trimmed text starts with
  `USER:` is.
- the first line is indented with no parent above it → ignored, and it is not the request.
- `  and the changelog` continues `USER: also update the docs`, so the final request is
  `also update the docs and the changelog` — the earlier request is not the answer.
- `  also check the fixture  ` continues a `TOOL` line; the tool name is unchanged.
- `TOOL` alone is not a call, so `calls` does not count it.
- `RESULT broken line without colon` is not a result.
- `write_file` is called and never produces a result, so `unresolved` is 1 even though
  `run_tests` was called after it and did produce one.

## Timebox

Four minutes. If you are past that, the approach is wrong.

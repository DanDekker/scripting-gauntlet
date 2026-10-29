# 145-agent-permission-boundary

> "Here is the tool-call trace from last night's agent run and the policy it was supposed
> to be held to. Which calls were actually inside the boundary, and what did each one
> break?"

## Input

`in/trace.jsonl` — one JSON object per line, a tool invocation:

```json
{"id": "inv-1", "tool": "read_file", "args": {"path": "src/app.py"}}
{"id": "inv-2", "tool": "bash", "args": {"cmd": "rm -rf /"}}
{"id": "inv-3", "tool": "http_get", "args": {"url": "https://api.github.com/repos"}}
```

`in/policy.json` — the capability policy:

```json
{
  "allowed_tools": ["read_file", "write_file", "bash", "http_get"],
  "allowed_domains": ["api.github.com", "pypi.org"],
  "banned_commands": ["rm -rf", "chmod 777", "mkfs", "dd if="]
}
```

## Rules

### 1. Which lines are invocations

Skip a line — and count it nowhere — when it is blank, not valid JSON, valid JSON that is
not an object, or an object whose `id` is missing, not a string, or the empty string.
Every other line is one **invocation**.

For a surviving invocation:

- `tool` is the record's `tool` when it is a string, and the empty string otherwise.
- `args` is the record's `args` when it is an object, and an empty object otherwise.

### 2. Violations

Check every rule and collect **all** that apply:

| violation | when |
| --- | --- |
| `banned-command` | `tool` is `bash` **and** `args.cmd` is a string containing any substring from `banned_commands` (case-sensitive) |
| `disallowed-domain` | `tool` is `http_get` **and** the host of `args.url` is not in `allowed_domains` |
| `path-traversal` | `args.path` is a string that starts with `/`, **or** whose `/`-split segments include a `..` |
| `unknown-tool` | `tool` is not in `allowed_tools` |

The **host** of a URL is: the text after `://`, up to the first `/`; then the part after the
last `@` (basic auth); then the part before the first `:` (port); lowercased. A URL with no
`://`, or a missing/ non-string `url`, gives the empty host `""`, which is not an allowed
domain.

`""`, `"."` and `"./src/app.py"` are **not** path traversal; `"/etc/shadow"`,
`"../../etc/passwd"` and `"src/../../secrets/key"` are.

### 3. Verdict

`allowed` when the invocation has zero violations, `denied` when it has one or more.

## Output

Write exactly these files to `$OUT`:

1. **`out/audit.csv`** — header `id,tool,verdict,violations`. One row per invocation,
   sorted by `id` ascending in **byte order** (so `inv-10` comes before `inv-2`). No field
   contains a comma or a quote, so plain comma separation is correct.
   - `tool` — the tool name, or empty when the record had no string `tool`
   - `verdict` — `allowed` or `denied`
   - `violations` — the violations joined with `;` in **alphabetical** order, or empty
2. **`out/summary.json`** — an object with exactly these keys:
   - `total_invocations` — invocations that survived step 1 (int)
   - `allowed_count` — invocations with verdict `allowed` (int)
   - `denied_count` — invocations with verdict `denied` (int)
   - `violations_count` — total violation **instances**, i.e. the sum over invocations of
     how many violations each has (int)

## Messes to expect

- the blank line, the `not json at all` line, the `[1, 2, 3]` array, the record with no `id`
  and the record with `"id": ""` are **not** invocations: the 27 non-blank lines
  (`trace.jsonl` has 28 lines, one of them blank) produce 23 invocations
- `inv-18` has no `tool` at all: it is `unknown-tool` **and** `path-traversal` at once, and
  its `tool` column is empty
- `inv-23` breaks two rules as well: its `args.path` is checked even though the tool is
  `bash`
- `inv-7` is an **allowed** `http_get`: basic auth, the `:443` port and the shouty
  `API.GitHub.com` all wash out of the host
- `inv-19` is denied: `api.github.com.evil.io` is not `api.github.com`
- `inv-8` is allowed: a banned path is not a banned command, and `banned-command` only
  looks at `bash`
- `inv-10`, `inv-11`, `inv-12`, `inv-17` are allowed: `"."`, an empty path, and a missing
  or non-object `args` are not violations
- `inv-16` is denied for `unknown-tool` even though its URL is on an allowed domain

## Timebox

Four minutes. If you are past that, the approach is wrong.

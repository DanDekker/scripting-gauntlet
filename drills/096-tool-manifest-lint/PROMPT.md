# 096-tool-manifest-lint

> "An agent is about to be handed these tools. Before that happens I want a list of every
> way each definition is broken — one line per problem, not one line per tool. If a tool is
> fine, I want to be able to prove it, not assume it."

## Input

`in/tools.json` — a JSON object mapping a tool name to its definition:

```json
{
  "read_file": {
    "description": "Read a file from the workspace",
    "parameters": {
      "type": "object",
      "properties": {"path": {"type": "string"}},
      "required": ["path"]
    }
  }
}
```

The file is messy in realistic ways: a tool whose `description` is only spaces, a tool whose
`description` is a number, a tool whose `required` names a property that was never declared,
optional properties that are legitimately *not* in `required`, a tool with no `parameters`
at all, a tool whose `parameters` is an array or a string, a tool name with a space and a
tool name with capitals, and two keys that appear twice in the raw text.

When a key appears twice in the raw JSON object, the **last** occurrence wins — that is what
any JSON parser does — so the definition you lint is the last one. The repeat itself is
still an error (`duplicate-key`), reported once for that tool name.

## Rules

A tool is one key of the top-level object after duplicate-key resolution. For every tool,
collect **every** code that applies (a tool may have several):

| code | when |
| --- | --- |
| `bad-name` | the tool name does not match `^[a-z0-9_]+$` |
| `no-description` | `description` is missing, is not a string, or is empty after trimming whitespace |
| `no-parameters` | `parameters` is missing, or is not a JSON object |
| `no-properties` | `parameters` is an object and `parameters.properties` is missing, not an object, or has no keys |
| `required-not-declared` | `parameters` is an object and an entry of `parameters.required` is not a key of `parameters.properties` |
| `undeclared-required` | `parameters.properties` has at least one key and `parameters.required` is missing entirely |
| `duplicate-key` | the tool name appears more than once in the raw JSON text |

Precise consequences of the rules above:

- The last four codes are only evaluated when `parameters` **is an object**. A tool with
  `"parameters": []` or `"parameters": "see the docs"` gets `no-parameters` and nothing else.
  A tool with no `parameters` key gets `no-parameters` and nothing else.
- `no-properties` and `required-not-declared` can fire together: a tool with no
  `properties` at all but with `"required": ["path"]` has every required entry undeclared.
  Treat a missing `properties` as an empty object when checking `required`.
- `required` is either absent or an array of strings. When it is absent, an empty
  `properties` object is *not* `undeclared-required` — that rule needs at least one property.
- A property that is present in `properties` but absent from `required` is **fine**: optional
  arguments are normal. It is not an error and must not be reported.
- `description` is trimmed before the emptiness test: `"   "` is `no-description`.

## Output

Write exactly these files to `$OUT`:

1. **`out/errors.csv`** — header `tool,code`. One row per (tool, code) pair, with `tool`
   spelled exactly as it appears in the manifest. Sorted by `tool` ascending (byte order,
   so `ReadURL` sorts before `Send Email` sorts before `delete_workspace`), then by `code`
   ascending. A tool with no errors produces no row. Duplicate (tool, code) pairs are
   reported once.
2. **`out/summary.json`** — an object with exactly these keys:
   - `tools` — distinct tool names after duplicate-key resolution (int)
   - `valid_tools` — tools with zero errors (int)
   - `invalid_tools` — tools with at least one error (int)
   - `errors` — total rows in `errors.csv` (int)

## Messes to expect

- parsing with a normal JSON library silently drops the repeated key: the duplicate is only
  visible in the raw text, and last-wins changes which definition you are judging
- `"parameters": []` is not an object, so it is `no-parameters`, not `no-properties`
- a tool with `properties` but no `required` is `undeclared-required`; a tool with `required`
  but no `properties` is `no-properties` *and* `required-not-declared`
- `description: 42` is not a string, so it is `no-description`
- `max_bytes` in `read_file` is declared but not required — that tool is clean

## Timebox

Four minutes. If you are past that, the approach is wrong.

# 116-tool-args

> "The model just called a tool and the call blew up. Before I let it retry, check every
> argument against the tool's own schema — every problem, named, not just the first one."

## Input

- `in/schema.json` — one tool schema, including the tool's own name:

  ```json
  {"name": "read_file",
   "type": "object",
   "properties": {"path":  {"type": "string"},
                  "mode":  {"type": "string", "enum": ["read", "write"]},
                  "limit": {"type": "integer", "minimum": 1}},
   "required": ["path"]}
  ```

  Only `name`, `properties` and `required` are read. A property may carry `type`,
  `enum` and/or `minimum`; it always carries `type` in this fixture.

- `in/calls.jsonl` — one model tool call per line:

  ```json
  {"call_id": "c1", "name": "read_file", "arguments": {"path": "a.txt"}}
  ```

## Rules

1. **Skip junk.** A blank line, a line that is not valid JSON, and a line that parses to
   something other than a JSON object are skipped. A skipped line is not a call and counts
   nowhere — not in `calls` and not in any counter.
2. **A record needs a name and an id.** An object is a record only when `name` is a string
   and `call_id` is a string. Anything else is skipped like junk.
3. **Wrong tool.** When `name` does not equal the schema's `name`, the call is status
   `wrong-tool`. It is *not* validated against the schema and produces no error rows.
4. **Bad arguments.** When a validated call has no `arguments` key, or its `arguments` value
   is not a JSON object, the call is status `bad-arguments`. It produces no error rows.
   (A call for the wrong tool is checked first: a wrong-tool call with a string
   `arguments` is still `wrong-tool`.)
5. **Otherwise validate.** For the remaining calls, produce one error per problem in this
   order of checks:
   1. `missing:<prop>` — a required property is absent. Required properties are checked in
      the order they appear in the schema's `required` list.
   2. `unknown:<prop>` — a property present in `arguments` that is not in the schema's
      `properties`. Checked in the order the properties appear in the arguments object
      (JSON document order).
   3. `type:<prop>` — the value does not match the declared `type`. Checked in arguments
      order. Types: `string` is a JSON string; `integer` is a JSON number with no
      fractional part (a JSON boolean is **not** a number); `number` is any JSON number (a
      boolean is **not** a number); `boolean` is a JSON boolean; `object` is a JSON object;
      `array` is a JSON array. A `null` value for an **optional** property is accepted and
      is not a type error. A `null` value for a required property is a type error.
   4. `enum:<prop>` — checked in arguments order, and only when the property's type is
      fine (and it is not an accepted optional `null`). The value must be one of the
      `enum` values.
   5. `min:<prop>` — checked in arguments order. The value is a JSON number, the schema has
      `minimum`, and the value is **less than** the minimum. A value equal to the minimum
      is fine.

   A call with zero errors is **valid**; a call with one or more errors is **invalid**.
   Every error is a separate row: a call can contribute several.

## Output

Write exactly these files to `$OUT`:

1. **`out/errors.csv`** — header `call_id,error`. One row per error and nothing else, in
   call order (the order the calls appear in the input file) and, within one call, in the
   check order above. `call_id` is the record's `call_id`. No field ever contains a comma,
   so no quoting is needed.
2. **`out/summary.json`** — an object with exactly these keys:
   - `calls` — records that survived rule 2 (int)
   - `valid` — calls with zero error rows (int). A `wrong-tool` or `bad-arguments` call has
     zero error rows, so it is counted here: `valid + invalid == calls`.
   - `invalid` — calls with at least one error row (int)
   - `errors` — total rows written to `errors.csv` (int)
   - `wrong_tool` — calls whose name did not match the schema (int)
   - `bad_arguments` — calls whose `arguments` was missing or not an object (int)

   Print it as one compact JSON object: `{"calls":21,"valid":10,...}`.

## Messes to expect

- `c2` has no `arguments` at all and `c3` has `"arguments": "path=a.txt"` — both are
  `bad-arguments`, and neither is a schema error
- `c4` misses `path`, `c18` passes `{}`, `c21` misses `path` *and* carries an unknown
  `extra` — missing errors come before unknown errors, so `c21` gets
  `missing:path` then `unknown:extra`
- `c5` carries an unknown `colour` between known properties
- `c6` sends a nested object where a string is expected; `c7` sends the string `"10"` for
  an integer; `c11` sends an object for `path`
- `c12` sends `true` for `limit` — a boolean is not an integer, so it is `type:limit`
- `c8` sends `limit: 0` (below `minimum: 1`); `c19` sends `limit: 1` (equal is fine)
- `c9` sends `mode: "append"` (not in the enum); `c10` sends `mode: null`, which is legal
  because `mode` is optional
- `c13` and `c14` are `write_file` calls — `wrong-tool`, including the one whose
  `arguments` is a string
- the line `this line is not json at all {"broken":`, the line `[1,2,3]`, the line
  `"just a string"` and the trailing-space line after `c16` are not records
- `c17` has no `name` and `c23` has a numeric `name` — both are skipped entirely
- `c16` has trailing spaces after the closing brace and still parses

## Timebox

Five minutes. If you are past that, the approach is wrong.

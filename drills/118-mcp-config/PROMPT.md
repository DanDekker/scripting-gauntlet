# 118-mcp-config

> "Someone pasted a new MCP config into the repo and wants the agent to launch it. Audit it
> first: which server entries would blow up at exec time, and which ones are weird enough
> that I want to know about them?"

## Input

- `in/mcp.json` — the config: an object whose `servers` object maps a server name to a
  launch spec.

  ```json
  {"servers": {"docs": {"command": "npx",
                        "args": ["-y", "docs-server"],
                        "env": {"API_KEY": "abc"}},
               "db": {"command": "python", "args": ["-m", "db"], "env": {}}}}
  ```

- `in/env.json` — an object of the environment variable names the machine actually
  defines, e.g. `{"API_KEY": "x", "HOME": "/root"}`. Only its key names matter.

## Rules

1. **Duplicate names come from the raw text.** When the JSON text contains the same server
   name twice, the **last** occurrence wins for parsing and the name is reported once as
   `duplicate-name`. Parsing the JSON normally already gives you last-wins; the report needs
   the raw text, because a JSON parser hides the collision.
2. **Every server gets every problem**, in exactly this order:
   1. `duplicate-name` — the name appeared more than once in the raw JSON. `detail` is the
      text `duplicate`. One row only, no matter how many extra copies there were.
   2. `bad-name` — the name does not match `^[a-z0-9_-]+$`. `detail` is empty.
   3. `missing-command` — there is no `command` key, or it is not a string. `detail` empty.
   4. `empty-command` — `command` is a string that is empty after trimming spaces, tabs and
      newlines. `detail` empty.
   5. `bad-args` — `args` is present but is not a list whose every element is a string.
      `detail` empty. A **missing** `args` key is fine and reports nothing.
   6. `undefined-env` — an `env` key names a variable that is not a key of `in/env.json`.
      One row per variable, in the order the variables appear in the `env` object,
      `detail` = the variable name. A missing or non-object `env` reports nothing.
   7. `unknown-key` — a key of the server object that is not `command`, `args` or `env`.
      One row per key, in the order the keys appear in the server object, `detail` = the
      key name.
3. A server with no problems is **valid**.
4. Server names are compared and sorted as byte strings (`LC_ALL=C` order): uppercase sorts
   before lowercase, and a space sorts before both.

## Output

Write exactly these files to `$OUT`:

1. **`out/problems.csv`** — header `server,problem,detail`. One row per problem, sorted by
   `server` ascending (byte order) and, inside one server, in the problem order above.
   `detail` is empty for every problem except `undefined-env` (variable name),
   `unknown-key` (key name) and `duplicate-name` (the word `duplicate`). No field contains
   a comma, so no quoting is needed.
2. **`out/summary.json`** — an object with exactly these keys:
   - `servers` — distinct server names after last-wins resolution (int)
   - `valid` — servers with no problems (int)
   - `invalid` — servers with at least one problem (int)
   - `problems` — total rows in `problems.csv` (int)

   Print it as one compact JSON object: `{"servers":12,"valid":3,...}`.

## Messes to expect

- `dup` appears twice in the raw JSON: last-wins leaves `{"command": "python3", ...}`,
  which is otherwise clean, so `dup` has exactly one row: `duplicate-name,duplicate`
- `Blank` and `Bad Args` fail `^[a-z0-9_-]+$` (uppercase letter, embedded space)
- `Blank` also has `"command": "   "` — a string, but empty after trimming, so it gets
  `empty-command` and **not** `missing-command`
- `ghost` has no `command` key at all; `empty` has `"command": ""`
- `Bad Args` has `"args": "not-a-list"` and `numargs` has `"args": ["a", 1]` — both
  `bad-args`; `noargs` has no `args` key and is therefore **valid**
- `db` references `MISSING_VAR`, `HOME` and `OTHER_MISSING`; only `HOME` is defined, so it
  gets two `undefined-env` rows in that order
- `shell` has an `autostart` key and `extra` has `autostart` then `cwd` — `unknown-key`
  rows in key order
- `docs` and `ok` are clean, `extra` is not

## Timebox

Four minutes. If you are past that, the approach is wrong.

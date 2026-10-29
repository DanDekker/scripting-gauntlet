# 113-template-vars

> "We ship prompts as templates and a JSON bag of values. Before this goes out I want the
> filled prompt, the exact number of holes nobody filled, and the values I'm carrying that
> the template never asks for."

## Input

- `in/template.txt` — a text template with `{{placeholder}}` holes. Any text, any number
  of lines.
- `in/values.json` — a JSON **object** mapping variable names to values. Values may be any
  JSON type: string, number, boolean, null, array or object.

The template is messy in realistic ways: a placeholder used twice, a placeholder with no
value and no default, a placeholder with no value but a default, values in `values.json`
that the template never uses, non-string values (number, boolean, null, array, object), a
placeholder with spaces inside the braces (`{{ name }}`), a placeholder split across two
lines, a dotted name (`{{user.name}}`), an empty `{{}}`, and a literal `{{` that never
closes.

## Rules

1. **What a placeholder is.** `{{` + optional spaces + a name + optional spaces + `}}`,
   where a name is one or more characters from `A-Z a-z 0-9 _ . -`. `{{}}` is **not** a
   placeholder. A `{{` with no matching `}}` on the **same line** is literal text.
2. **Defaults.** A placeholder may carry a default: `{{name|default}}`. The text before the
   **first** `|` is the name; the text after it, trimmed of spaces, is the default. A default
   may be empty (`{{name|}}`).
3. **No spanning lines.** Placeholders never cross a line boundary: a `{{` on one line and a
   `}}` on the next are literal text on both lines.
4. **Resolution**, first match wins:
   - `values.json` has the key → use that value (even when it is `null` or `false`);
   - otherwise the placeholder has a default → use the default;
   - otherwise the occurrence is a **HOLE**.
5. **Rendering a value.** A string is used verbatim. A number, boolean or null is rendered
   as its JSON text: `42`, `0.75`, `true`, `null`. An array or object is rendered as its
   **compact** JSON text — no spaces after `,` or `:`, e.g. `["a","b"]`,
   `{"k":"v"}`.
6. **Holes.** A HOLE is rendered as the literal text `[MISSING:name]`.
7. **Everything else is preserved byte for byte**, including indentation, blank lines and
   stray braces.

## Output

Write exactly these files to `$OUT`:

1. **`out/rendered.txt`** — the filled template. Every character of the template that is
   not a placeholder survives unchanged. The file ends with a newline **iff** the template
   did.
2. **`out/summary.json`** — an object with exactly these keys:
   - `placeholders` — placeholder occurrences in the template, counting a repeated name once
     per occurrence (int)
   - `distinct` — distinct placeholder names (int)
   - `holes` — occurrences that resolved to nothing, i.e. neither a value nor a default (int)
   - `unused` — keys of `values.json` that no placeholder names, sorted ascending (list of
     strings; `[]` when there are none)
   - `defaults_used` — occurrences resolved from a default (int)

## Messes to expect

- `{{}}` renders as the literal `{{}}`; the line with a lone `{{` keeps its `{{` untouched
- `{{split_` / `name}}` on consecutive lines are literal text on both lines — the split name
  is neither a placeholder nor an unused-value reference
- `{{ owner }}` with no `owner` key and no default is `[MISSING:owner]` and counts as a hole
- `{{ contact|ops@example.com }}` uses the default, trimmed, and counts in `defaults_used`
- `{{nope|}}` resolves to the empty string — it is *not* a hole
- `cache` is `null`: it renders as `null`, not as a hole and not as an empty string
- `tags` and `config` render as compact JSON, never as a Python/awk repr
- the names `debug` and `unused_key` exist in `values.json` and appear in `unused`

## Timebox

Four minutes. If you are past that, the approach is wrong.

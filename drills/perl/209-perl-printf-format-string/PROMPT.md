# 209-perl-printf-format-string

> "Our status report came out as `Deploy: 100omplete` and `Disk: 85 0.000000ull`. The
> generator did `printf \"$template\\n\"` — so the template's own percent sign became a
> conversion specifier and ate the text after it."

## Input

`in/templates.txt` — one status template per line:

```text
Deploy: 100% complete
Disk: 85% full
Queue: 0 pending
```

## Rules

1. Read `in/templates.txt`, one template per line.
2. **`out/report.txt`** — the templates, one per line, **exactly as they appear in the
   input**. A percent sign in a template is a literal character of the template, not a
   conversion specifier, and the text after it must survive.
3. **`out/summary.json`** — keys `templates`, `percent_templates`, `chars`. One compact
   JSON object.
   - `templates` — the number of templates.
   - `percent_templates` — the number of templates that contain a `%` character.
   - `chars` — the total number of characters in all the templates, **not counting the
     line terminators**.

## Messes to expect

- `printf` and `sprintf` read their **first argument** as the format string. Writing
  `printf "$template\n"` hands the data to the format parser, so `% c` consumes the
  character after the percent sign and `% f` prints `0.000000`.
- `printf '%s\n', $template` prints the template literally and is the safe form.

## Timebox

Four minutes.

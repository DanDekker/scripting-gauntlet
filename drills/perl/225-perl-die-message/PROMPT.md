# 225-perl-die-message

> "The report said `disk full at app.pl line 12.` — the error text the operator wanted to
> match was `disk full`, but perl bolts ` at FILE line N.` onto a `die` unless the
> message ends with a newline."

## Input

`in/checks.txt` — one check per line, `<name> <message>`:

```text
disk disk full
net network unreachable
mem out of memory
```

## Rules

1. Read `in/checks.txt`, one check per line. The name is the first word, the message
   is the rest of the line.
2. For each check, raise the message as a perl error and catch it.
3. Report the **message text** of the caught error:
   - the text exactly as the check file gives it;
   - with **no** ` at FILE line N.` suffix;
   - with no trailing newline.
4. **`out/checks.csv`** — header `index,name,message`. One row per check, in file order,
   `index` starting at 1.
5. **`out/summary.json`** — keys `checks`, `longest`, `first`. One compact JSON object.
   - `checks` — the number of checks.
   - `longest` — the length in characters of the longest reported message.
   - `first` — the message of the first check.

## Messes to expect

- `die "text"` appends ` at FILE line N.` to the message, because perl adds the
  location when the message does not end with a newline.
- `die "text\n"` has **no** location appended, so the caught message is exactly the
  text plus a newline — strip that newline and nothing else.
- The caught error is in `$@`.

## Timebox

Four minutes.

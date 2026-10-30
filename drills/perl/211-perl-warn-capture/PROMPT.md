# 211-perl-warn-capture

> "The log collector started capturing warnings that were supposed to reach the
> terminal. The handler was installed as `$SIG{__WARN__} = sub { ... }` — a global
> assignment — so it stayed installed for the rest of the program. The messages also
> came out as `disk nearly full at app.pl line 12.` because `warn` adds the location
> unless the message ends with a newline."

## Input

`in/warnings.txt` — the warning messages to emit, one per line:

```text
disk nearly full
cache miss for alpha
rotation started
```

## Rules

1. Read `in/warnings.txt`, one message per line.
2. **Watched phase.** Install a warning handler that records the warnings it receives.
   While the handler is installed, emit each message from `in/warnings.txt` with
   `warn`, so it goes to the handler instead of to stderr.
   - Emit each message **with a trailing newline**, so that Perl does not append
     ` at FILE line N.` to it. The recorded message is then exactly the text from the
     file, without its trailing newline.
   - The handler must be installed so that it is **removed again** when the watched
     phase ends.
3. **After the watched phase.** Emit one more warning, `rotation complete`, with a
   trailing newline. It must **not** be captured by the handler.
4. **`out/warnings.csv`** — header `index,message`. One row per captured warning, in
   the order captured, `index` starting at 1, `message` the message text without its
   trailing newline.
5. **`out/summary.json`** — keys `emitted`, `captured`, `final_captured`. One compact
   JSON object.
   - `emitted` — the number of warnings emitted in total (the ones from the file plus
     the final one).
   - `captured` — the number of warnings the handler recorded.
   - `final_captured` — `true` if the final warning was captured by the handler, else
     `false`.

## Messes to expect

- `warn "text"` without a trailing newline becomes `text at FILE line N.` — the
  location suffix is part of the message the handler receives.
- `$SIG{__WARN__} = sub { ... }` is a **global** assignment. `local $SIG{__WARN__} = ...`
  restores the previous handler when the enclosing block ends.

## Timebox

Five minutes.

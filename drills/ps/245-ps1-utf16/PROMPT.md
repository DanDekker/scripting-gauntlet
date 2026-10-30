# 245-ps1-utf16

> "The collector wrote this event log from a Windows host. Count the levels and keep
> the accented message intact."

## Input

The setup hook creates in/events.log as UTF-16LE without a byte-order mark. Its logical
content is:

~~~text
INFO|job started
WARN| café cache low 

ERROR|disk full
INFO|job done
~~~

Blank lines are not records. The file is deliberately encoded differently from the
PowerShell 7 default.

## Rules

1. Read events.log as UTF-16LE.
2. Skip blank lines and trim surrounding whitespace from each field.
3. Split each record on one literal pipe into level and message.
4. Keep input order and preserve the accented character.

## Output

Write exactly:

1. out/events.csv with header level,message and four rows.
2. out/summary.json with exactly
   {"records":4,"info":2,"warn":1,"error":1}.

## Messes to expect

- the input has no BOM, so encoding auto-detection cannot save a default read
- decoding UTF-16LE as UTF-8 leaves NUL characters in the text
- the blank physical line is not an event
- café must remain café, not replacement characters

## Timebox

Four minutes. On PowerShell, use Get-Content -Encoding Unicode; in .NET, Unicode means
little-endian UTF-16.

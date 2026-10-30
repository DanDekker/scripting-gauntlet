# 257-tcl-regexp-records

> "Extract the structured events from this mixed log and tell me which ones are
> slow. Noise is expected and should be counted, not turned into a fake event."

## Input

in/events.log contains:

~~~text
[INFO] worker=api.v2 duration=12ms
[WARN] worker=web duration=0ms
noise line
[ERROR] worker=db duration=305ms
~~~

## Rules

1. Accept only the whole-line shape
   [INFO|WARN|ERROR] worker=<letters, digits, dot, underscore, or dash>
   duration=<digits>ms.
2. Emit accepted records in input order. Skip malformed lines and count them.
3. duration is an integer. slow is yes when duration is greater than 100, otherwise
   no.

## Output

Write out/events.csv with header level,worker,duration,slow and three rows.
Write out/summary.json with exactly {"records":3,"skipped":1,"slow":1}.

## Messes to expect

- the noise line must not reuse captures from a previous successful match
- the regex is anchored at both ends
- duration 0 is a valid integer
- Tcl regexp returns a success Boolean; branch on it before using captures

## Timebox

Five minutes. Use regexp with capture variables and test its return value.

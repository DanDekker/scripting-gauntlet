# 251-jxa-date-timezone

> "Normalize these timestamp strings to UTC. The offsets are part of the data, and
> one calendar date is impossible."

## Input

in/stamps.csv has id and stamp:

~~~csv
id,stamp
a,2026-03-08T01:30:00-07:00
b,2026-11-01T01:30:00-06:00
epoch,1970-01-01T00:00:00Z
bad,2026-02-29T12:00:00Z
offset,2026-10-30T17:45:00+05:30
~~~

## Rules

1. Parse the exact ISO shape with a non-lenient NSDateFormatter using an
   en_US_POSIX locale.
2. Keep valid rows in input order. Reject the impossible date and count it.
3. Emit UTC as yyyy-MM-ddTHH:mm:ssZ and epoch as integer seconds.
4. Epoch zero is valid.

## Output

Write out/stamps.csv with header id,utc,epoch and the four valid rows.
Write out/summary.json with exactly {"accepted":4,"rejected":1,"epoch_zero":1}.

## Messes to expect

- the two 01:30 values have different explicit offsets
- the host's local timezone must not affect the result
- NSDateFormatter is lenient unless told otherwise
- epoch 0 is a real timestamp, not a missing value

## Timebox

Five minutes. Set locale, format, lenient=false, and then switch the formatter timezone
to UTC only for output.

# 242-ps1-tryparse

> "Some measurements are empty or malformed, but zero is a valid reading. Parse the
> integer rows without turning a failed conversion into a fake zero."

## Input

in/measurements.csv has columns name,raw. raw may contain surrounding whitespace:

~~~csv
name,raw
zero,0
spaced,  17
negative,-3
padded,0005
bad-decimal,1.5
blank,
word,unknown
huge,99999999999999999999
~~~

## Rules

1. Trim raw and parse it as a signed 32-bit invariant integer.
2. Keep accepted rows in input order. Do not round decimals, wrap overflow, or turn
   blank input into zero.
3. Count every rejected row, but do not emit it.

## Output

Write exactly:

1. out/readings.csv with header name,value and the four accepted rows.
2. out/summary.json with exactly
   {"accepted":4,"rejected":4,"total":19}.

## Messes to expect

- 0 is a valid value even though it is falsy in PowerShell
- a TryParse call returns a Boolean and writes the parsed value through [ref]
- a blank string and an overflow value must be rejected
- a decimal string is not an integer and must not be rounded

## Timebox

Five minutes. Use the overload that takes NumberStyles, InvariantCulture, and a
[ref] result variable.

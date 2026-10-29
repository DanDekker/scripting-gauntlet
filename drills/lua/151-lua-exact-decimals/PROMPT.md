# 151-lua-exact-decimals

> "These sensor readings come in as text and I need exact totals. Last time a float sum
> drifted and the dashboard showed a number nobody could reproduce."

## Input

`in/measurements.csv` — a header line `sensor,value`, then one reading per line:

```
sensor,value
alpha,42
alpha,42.5
```

The readings are plain decimals, but some are integers, some have a sign, some have one
to three decimal places, and one is not a number at all.

## Rules

1. Skip the header line. Every other line is one reading: `sensor` then `value`,
   separated by a comma. Trim whitespace around both.
2. A **value** is valid when it matches `-?DIGITS` or `-?DIGITS.DIGITS` with one to
   three digits after the point. The optional sign may also be `+`. Anything else is
   **invalid**: count it and skip it. A reading whose `sensor` is empty is invalid too.
3. Scale every valid value to **integer thousandths**: `42` is `42000`, `42.5` is `42500`,
   `-0.25` is `-250`. Do the scaling with integer arithmetic on the digits; do not go
   through a floating point value.
4. Group by sensor. For each sensor report the number of readings, and the smallest,
   largest and total of the scaled values.
5. **Print every scaled value as a decimal with exactly three places**: the integer part,
   a point, then the remainder zero-padded to three digits — `42` prints as `42.000`,
   `-0.25` as `-0.250`, `0` as `0.000`. A negative value keeps its sign; `-0.250` is not
   `0.250`.

## Output

Write exactly these files to `$OUT`:

1. **`out/sensors.csv`** — header `sensor,count,min,max,total`, then one row per sensor,
   sorted by sensor ascending in **byte order**. The four numeric columns after the count
   are printed as in rule 5.
2. **`out/summary.json`** — an object with exactly these keys:
   - `sensors` — how many sensors have at least one valid reading (int)
   - `records` — how many readings were valid (int)
   - `invalid` — how many readings were invalid (int)
   - `total` — the total of every valid reading, printed as in rule 5 (string)

   Print it as one compact JSON object: `{"sensors":3,"records":6,...}`.

## Messes to expect

- `-0.25` is a negative scaled value, and the remainder of a negative division needs the
  sign handled separately
- `42` has no point at all and still prints three places
- `gamma,0.125` keeps all three of its decimals
- `delta,abc` is invalid: it is counted and it contributes nothing to any total

## Timebox

Five minutes. Integer arithmetic on the digits is the whole trick; if you are reaching
for a float formatter, the approach is wrong.

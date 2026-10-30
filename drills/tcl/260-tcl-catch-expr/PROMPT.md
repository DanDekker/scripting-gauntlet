# 260-tcl-catch-expr

> "Compute these ratios. Bad numbers and a zero denominator are expected input
> errors; report them and continue."

## Input

in/ratios.csv has columns id,numerator,denominator:

~~~csv
id,numerator,denominator
whole,10,2
zero,10,0
bad,foo,3
negative,7,-2
~~~

## Rules

1. Parse the numeric fields as decimal numbers.
2. Compute a successful ratio as numerator divided by denominator, formatted with
   exactly two decimal places.
3. A zero denominator or nonnumeric field is rejected and counted; it produces no row.
4. Preserve input order.

## Output

Write out/ratios.csv with header id,ratio and rows:

~~~csv
whole,5.00
negative,-3.50
~~~

Write out/summary.json with exactly {"accepted":2,"rejected":2}.

## Messes to expect

- expr errors are Tcl errors that catch can turn into a per-row decision
- integer division would lose the .50 in 7 / -2
- zero is a valid numerator but not a valid denominator
- do not emit a fake zero for rejected input

## Timebox

Five minutes. Wrap the numeric expression in catch and force floating-point division.

# 256-tcl-dict-presence

> "This tiny settings file has a real zero, an empty owner, a false-looking string,
> and one key that is absent. Report the states without calling dict get on a key
> that does not exist."

## Input

in/settings.tsv has tab-separated key/value rows:

~~~text
limit	0
owner	
enabled	false
~~~

The required keys, in reporting order, are limit, owner, enabled, and region. region
does not appear in the input.

## Rules

For each required key:

1. state is missing when the key is absent.
2. state is empty when the key exists and its value is empty.
3. state is zero when the key exists with exactly the value 0.
4. state is value for every other present value, including the string false.
5. value is empty for missing or empty keys; otherwise preserve the trimmed text.

## Output

Write out/settings.csv with header key,state,value and four rows.
Write out/summary.json with exactly
{"keys":4,"missing":1,"empty":1,"zero":1}.

## Messes to expect

- dict exists is the safe presence test before dict get
- Tcl if treats 0 and the empty string as false, but they are different data states
- the text false is a present value, not a missing key
- report order is explicit, not dict iteration order

## Timebox

Five minutes. Build a dict, use dict exists first, and compare values with string
operators where the contract is textual.

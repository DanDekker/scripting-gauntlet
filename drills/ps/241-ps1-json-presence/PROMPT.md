# 241-ps1-json-presence

> "The JSON feed uses absence, null, empty text, and zero differently. Give me a
> report that preserves those distinctions instead of collapsing everything falsy."

## Input

in/records.json is an array of objects:

~~~json
[
  {"id":"alpha","owner":null,"quota":0},
  {"id":"beta","quota":5},
  {"id":"gamma","owner":"","quota":null},
  {"id":"delta","owner":"  Ada  ","quota":12},
  {"id":"epsilon","owner":"0","quota":-2}
]
~~~

All records have a nonempty id. The owner and quota properties are deliberately
different kinds of missing or falsy values.

## Rules

For every record, preserve input order.

1. owner_state is missing, null, empty, or value.
   - missing means the property is absent.
   - null means the property is present with JSON null.
   - empty means a string becomes empty after trimming.
   - value means any other value. Trim string values for owner_value.
2. quota_state is missing, null, zero, positive, or negative.
   The fixture uses integer numbers. Preserve a numeric quota in quota_value; leave
   quota_value empty for missing or null.
3. Do not use truthiness as a substitute for any of these tests. Zero and the string
   0 are real values.

## Output

Write exactly these files to $OUT:

1. out/report.csv with header
   id,owner_state,owner_value,quota_state,quota_value
2. out/summary.json with exactly these integer keys:
   records, owner_missing, owner_null, owner_empty, quota_missing, quota_null.

Expected summary:

~~~json
{"records":5,"owner_missing":1,"owner_null":1,"owner_empty":1,"quota_missing":0,"quota_null":1}
~~~

## Messes to expect

- an absent JSON property is not the same as a present property whose value is null
- an empty string is not the same as a missing property
- numeric zero is falsy in PowerShell but still a quota value
- "0" is a nonempty string, and surrounding whitespace must be trimmed

## Timebox

Five minutes. Inspect PSObject.Properties to test presence before reading .Value.

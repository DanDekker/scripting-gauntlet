# 248-jxa-json-bridge

> "This macOS helper reads a JSON export through Foundation. Preserve the difference
> between a missing owner, a JSON null owner, and a real owner."

## Input

in/records.json contains:

~~~json
[
  {"id":"a","tags":["mac","prod"],"owner":null,"enabled":true},
  {"id":"b","tags":[],"owner":"  Lee ","enabled":false},
  {"id":"c","tags":["mac"],"enabled":true}
]
~~~

Read it with NSJSONSerialization. The owner property is intentionally absent in the
last record and explicitly null in the first.

## Rules

1. Preserve input order.
2. owner_state is null, missing, or value. Trim a string owner into owner.
3. Preserve tags and enabled exactly.
4. Count records with a null owner, a missing owner, and at least one tag.

## Output

Write out/report.json with exactly this shape:

~~~json
{
  "records":[
    {"id":"a","owner_state":"null","owner":"","tags":["mac","prod"],"enabled":true},
    {"id":"b","owner_state":"value","owner":"Lee","tags":[],"enabled":false},
    {"id":"c","owner_state":"missing","owner":"","tags":["mac"],"enabled":true}
  ],
  "summary":{"records":3,"null_owner":1,"missing_owner":1,"tagged":2}
}
~~~

No extra keys or files.

## Messes to expect

- an NSDictionary-backed JSON object can contain NSNull
- a missing key is not the same as a key whose value is null
- ObjC.deepUnwrap is useful for nested Foundation arrays and dictionaries
- JXA runs through osascript and is macOS-only

## Timebox

Five minutes. Parse with Foundation, deep-unpack once, then use JavaScript presence
checks on the resulting object.

# 252-jxa-plist-write

> "The next macOS tool expects a property list, not JSON. Convert this small settings
> export into a readable XML plist with its native types intact."

## Input

in/settings.json contains:

~~~json
{
  "name":"agent",
  "enabled":true,
  "retry":3,
  "note":"café",
  "labels":["mac","ops"],
  "limits":{"soft":10,"hard":20}
}
~~~

## Rules

1. Parse the JSON with Foundation.
2. Serialize the same property-list-compatible object with
   NSPropertyListXMLFormat_v1_0.
3. Keep strings, booleans, integers, arrays, and nested dictionaries as their native
   plist types. Do not stringify the object.

## Output

Write exactly one file: out/report.plist. It must be a valid XML property list whose
root dictionary has exactly the six input keys and values.

## Messes to expect

- a file named report.plist is not valid merely because its contents are JSON
- JSON text has no typed plist representation until Foundation serializes the native
  NSDictionary/NSArray graph
- XML output makes the result inspectable by macOS tools
- non-ASCII text must survive the bridge

## Timebox

Four minutes. Feed the NSDictionary returned by NSJSONSerialization directly into
NSPropertyListSerialization.

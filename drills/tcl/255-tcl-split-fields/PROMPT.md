# 255-tcl-split-fields

> "This pipe feed has empty fields. Normalize it without losing the blank tag or the
> row whose name is empty."

## Input

in/records.psv is a literal-pipe feed:

~~~text
id|name|tag
1|Alpha|
2|Beta|  x 
3||y
4|Gamma| 
~~~

## Rules

1. Skip the header and blank physical lines.
2. Split on the literal pipe into exactly three fields. Tcl split preserves empty
   fields, including a trailing one.
3. Trim each field but keep the row and the empty value.
4. tag_state is empty when tag is empty, otherwise value. Preserve input order.

## Output

Write out/records.csv with header id,name,tag,tag_state and four rows.
Write out/summary.json with exactly
{"records":4,"empty_tag":2,"blank_name":1}.

## Messes to expect

- a trailing delimiter is an empty field, not a missing row
- one record has an empty middle field
- whitespace around x and the final tag must be trimmed
- Tcl lists retain empty elements when split

## Timebox

Four minutes. Use split and lassign on a Tcl list, not a regular expression that
requires every field to contain a character.

# 250-jxa-path-inventory

> "Inventory these manifest paths from a macOS handoff directory. Some are hidden,
> nested, or begin with a dash."

## Input

in/manifest.txt lists these relative paths in order:

~~~text
-dash.txt
.hidden
reports/one.txt
reports/two file.txt
~~~

The matching files are under in/tree. The path strings are literal data; do not
discover extra files or change their order.

## Rules

1. Compose each path relative to in/tree with a Foundation path API.
2. Read each file's regular-file byte size from NSFileManager attributes.
3. Emit four rows in manifest order.

## Output

Write out/inventory.csv with header path,bytes,kind. kind is always file.
Write out/summary.json with exactly {"files":4,"bytes":25}.

## Messes to expect

- one file is nested below the top-level directory
- one file is hidden and one begins with a dash
- the filename contains a space
- directory enumeration is not a substitute for following the manifest

## Timebox

Four minutes. NSString.stringByAppendingPathComponent and
NSFileManager.attributesOfItemAtPathError are the useful Foundation calls.

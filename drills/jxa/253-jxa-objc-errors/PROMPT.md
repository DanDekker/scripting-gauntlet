# 253-jxa-objc-errors

> "Check these three paths. A missing file is an expected result to report, not a
> reason to abort the whole inventory."

## Input

in/jobs.csv has id and path:

~~~csv
id,path
one,files/one.txt
empty,files/empty.txt
missing,files/nope.txt
~~~

The first file contains six bytes including its final newline, the second exists and is empty, and the third
does not exist.

## Rules

1. Resolve each path relative to in.
2. Call NSFileManager.attributesOfItemAtPathError for each row.
3. A successful attribute lookup is status ok with its byte count.
4. A nil result with an NSError is status missing with zero bytes. Continue to the next
   row; do not print the OS error text.
5. Preserve input order.

## Output

Write out/checks.csv with header id,status,bytes,message. message is empty for both
ok rows and not found for the missing row.
Write out/summary.json with exactly {"jobs":3,"ok":2,"missing":1,"bytes":6}.

## Messes to expect

- Foundation methods return nil plus an NSError through Ref(); they do not throw a
  JavaScript exception for a missing path
- an empty file has a valid byte count of zero
- continue after an expected per-row failure
- do not leak localized OS error text into a stable report

## Timebox

Five minutes. Allocate a fresh Ref() for each call and branch on the returned
attributes object.

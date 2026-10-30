# 247-ps1-format-object

> "Give the deployment bot a CSV report, not a pretty console table. It needs the
> actual columns and values for the next step."

## Input

in/services.csv has columns name, status, latency_ms, and owner:

~~~csv
name,status,latency_ms,owner
api,up,12,platform
worker,down,0,jobs
web,up,120,frontend
~~~

## Rules

1. Parse the input as objects.
2. Add healthy = yes only when status is up and latency_ms is at most 100; otherwise
   healthy = no.
3. Preserve input order and emit the named values as data. Do not emit a formatted
   table or display decorations.

## Output

Write exactly:

1. out/report.csv with header name,status,latency_ms,owner,healthy.
2. out/summary.json with exactly
   {"services":3,"healthy":1,"down":1,"slow":1}.

## Messes to expect

- Format-Table produces display objects and column separators, not CSV fields
- a down service with latency 0 is still unhealthy
- an up service above 100 ms is slow and unhealthy
- Export-Csv needs objects with deliberate property names

## Timebox

Four minutes. Keep the pipeline as objects until Export-Csv.

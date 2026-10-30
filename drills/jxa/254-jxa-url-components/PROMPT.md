# 254-jxa-url-components

> "Classify these saved URLs without making a request. Foundation should tell me the
> host, port, path, and number of query parameters."

## Input

in/urls.csv has id and url:

~~~csv
id,url
search,https://example.test:8443/api/search?q=mac%20tools&tag=jxa
file,file:///Users/dd/Library/Application%20Support/app/data.json
health,https://example.test/health
bad,not a url
~~~

## Rules

1. Parse each URL with NSURLComponents. Do not contact any host.
2. A valid row has a scheme and either a host or the file scheme. Skip malformed rows.
3. Report the path as NSURLComponents exposes it, the numeric port when present, and
   the number of query items.
4. Preserve valid input order and count skipped rows.

## Output

Write out/urls.csv with header id,scheme,host,port,path,query_items and one row per
valid URL.
Write out/summary.json with exactly {"urls":3,"skipped":1,"query_params":2}.

## Messes to expect

- query values are percent-encoded but query item count is structural
- a file URL has no host or port and is still valid
- a bare phrase is not a URL just because it is a string
- NSURLComponents avoids hand-splitting scheme, authority, and query text

## Timebox

Five minutes. Use NSURLComponents.componentsWithString and inspect its components
instead of writing a URL parser.

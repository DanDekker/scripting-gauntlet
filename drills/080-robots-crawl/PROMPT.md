# 080-robots-crawl

> "I have a URL list and a robots.txt. Before the crawler touches anything, tell me which
> URLs it may fetch and which rule stops each one."

## Task

`in/robots.txt` is a saved robots file. `in/urls.txt` is the crawl list, one URL per line.
The crawler identifies itself as `ScriptBot`.

## Rules

1. In `robots.txt`, strip `#` comments, ignore blank lines. A group is one or more
   `User-agent:` lines followed by its `Allow:`/`Disallow:` rules; a new `User-agent:`
   after rules start a new group.
2. Use the group whose agent equals `ScriptBot` case-insensitively. If there is none, use
   the `*` group. **Never merge** the two groups.
3. For each URL, match against the path **plus query string** (drop scheme, host and
   fragment). A URL with no path counts as `/`.
4. A pattern matches when it matches a **prefix** of that path+query, where `*` matches
   any run of characters and a `$` as the last character anchors the end. Every other
   character is literal.
5. The rule with the **longest pattern** wins. On equal length, `Allow` wins. No matching
   rule means allowed.
6. Skip blank and `#` lines in `in/urls.txt`.

## Output

- `out/crawl.csv` - header `url,allowed,rule`, one row per URL sorted ascending by `url`
  in byte order. `allowed` is `yes` or `no`; `rule` is the winning pattern, or empty when
  no rule matched.
- `out/summary.json` - exactly three integers: `urls`, `allowed`, `disallowed`.

## Messes to expect

- a `*` group that disallows everything, which must be ignored for ScriptBot
- `Disallow: /admin` also catching `/adminish`
- `/*.pdf$` blocking a bare PDF but not one with a query string
- a URL with no path at all

## Timebox

5 minutes. Compile each pattern to an anchored regex once, then test it per URL.

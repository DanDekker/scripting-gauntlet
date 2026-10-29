# 129-crawl-frontier

> "We saved a chunk of the site's link graph before the box went away. Walk it like a
> crawler would: breadth-first, no loops, mind the depth cap and the page cap — and tell
> me exactly what you refused to follow."

## Input

`in/sitemap.txt` is a saved link graph. A line whose trimmed text is an absolute
`http://` or `https://` URL starts a page block; the `<a href="...">` lines under it are
that page's links, in document order, until the next page line. Any other line is noise.

`in/config.json`: `{"seed": str, "max_depth": int, "same_host": str, "limit": int}`.

## Rules

1. **Page identity.** A URL is normalised by trimming it and removing everything from the
   first `#`. `http://x/p#a` and `http://x/p#b` are the same page. `http://x/dir` and
   `http://x/dir/` are **different** pages. A query string is part of the identity.
2. **The page set** is every line that is an absolute `http://`/`https://` URL after that
   normalisation. Blank lines, the `<a href>` lines, and lines that are not absolute URLs
   are not pages. Duplicates collapse into one page, and a page that appears more than
   once keeps one link list: the occurrences are **concatenated in file order**. The order
   of the sitemap does not affect visit order — only discovery order does.
3. **Links.** A page's links are the absolute `http(s)` URLs in its own `<a href="...">`
   lines, in document order, with the fragment stripped and with the page's own URL
   removed. A relative href, or a line with no href, is not a link at all — it is neither
   followed nor counted as skipped.
4. **Breadth-first.** The crawl starts at the seed (normalised the same way) at depth 0.
   If the seed is not in the page set, nothing is visited. Process the frontier in order
   of increasing depth; within a depth, in the order pages were discovered. The depth of a
   page is the depth at which it was first discovered.
5. **Following.** A link is followed only when it is in the page set **and** it has not
   been visited **and** it has not already been discovered (queued) **and**, when
   `same_host` is non-empty, its host equals `same_host` exactly. The host is the text
   between `://` and the first `/`; a port is part of the host. Every link that fails any
   of those tests is **skipped** and counted once per occurrence. Links to the page itself
   are excluded by rule 3 and are never counted as skipped.
6. **Stopping.** A page at `max_depth` contributes no new links: its links are never
   examined, so they cannot be skipped. `limit` is a hard cap — when the `limit`-th page
   is visited the crawl ends, the rest of the frontier is abandoned without being counted
   as skipped, and the `limit`-th page's own links are not examined.

## Output

**`out/pages.csv`** — header `url,depth,inbound`, then one row per **visited** page in
visit order (which is discovery order).

- `url` is the normalised URL.
- `depth` is the depth at which it was first discovered; the seed is `0`.
- `inbound` is the number of **distinct pages in the whole page set** (not just the
  visited ones) whose link list contains this URL. A page never counts itself.

**`out/summary.json`** — an object with exactly these keys:

| key | meaning |
|---|---|
| `visited` | pages visited (= rows in `pages.csv`) |
| `skipped` | link occurrences that were not followed, per rule 5 |
| `limit_reached` | boolean: `true` only when the crawl ended with pages still queued because `limit` was hit |
| `max_depth_reached` | the greatest depth among visited pages (`0` when nothing was visited) |
| `orphan` | pages in the page set that were never visited and are not the seed |

## Messes to expect

- blank lines inside and between blocks, one URL line padded with spaces and a trailing
  tab, a page line repeated later in the file (it merges, it does not duplicate)
- `#fragment` links that collapse onto an already-known page, including a link that
  collapses onto the page's own URL
- `http://example.com/dir` next to `http://example.com/dir/` — two different pages
- a link to a URL that is not in the page set, a link to another host, a relative href
- a line that is not a URL at all in the middle of the graph
- the depth cap and the page cap both biting in the same crawl

## Timebox

5 minutes. In python, a `deque` of `(url, depth)` is the whole crawler. In bash, do the
BFS in `awk` with two parallel queue arrays — bash 3.2 has no associative arrays.

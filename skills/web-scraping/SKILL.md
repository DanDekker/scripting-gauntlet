---
name: web-scraping
description: Extract structured data from HTML you do not own, using html.parser, scoped regular expressions, or a headless browser when the page renders client-side. Use when asked to pull a table, prices, listings, or fields from a saved page or a live URL, to monitor a page for changes, or when someone hands you HTML and wants rows out of it. Not for building crawlers at scale or bypassing access controls.
license: MIT
metadata:
  family: web-scraping
  drill: 004-scrape-table
---

# Web scraping

Markup is a tree, not a text file. Treat it as text and you will ship a parser that works
until the first `<span>` appears.

## Save first, parse second

```bash
curl -fsS -o page.html "$URL"     # then work from the file
```

Iterate against the saved copy. Every re-fetch is a new variable (A/B tests, lazy loading,
rate limits) between you and a correct answer.

## Scope the parser to one subtree

Find the smallest container that holds the data — `<table id="pricing">`, `<main>`,
`data-testid` — and parse only that. Whole-document regexes match the mobile duplicate,
the footer, and last year's markup.

```python
class Table(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)   # decodes &amp; for you
        self.inside = False
        self.rows, self.cell = [], None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "table" and attrs.get("id") == "pricing":
            self.inside = True
        elif self.inside and tag == "td":
            self.cell = []

    def handle_data(self, data):
        if self.inside and self.cell is not None:
            self.cell.append(data)
```

When you must regex, anchor on a *stable unique* token (`id=`, a data attribute, a class
that names the thing) — never on visual position or inline styling.

## Cell hygiene

Every cell you extract needs the same three moves, in this order:

1. **Drop decoration** — badges, icons, tooltips (`<span class="badge">`).
2. **Strip inline tags**, then **decode entities** (`&amp;` → `&`, `&nbsp;` → space).
3. **Collapse whitespace** and trim — markup indentation is not data.

## Numbers

Prices arrive as `$2,499`, `2 499 €`, `From $49/mo`. Strip currency symbols and thousands
separators, decide what a missing value means, then parse. Never let an unparsed string
silently become `NaN` in your output.

## Traps

- **Hidden or duplicate markup.** Responsive sites ship two copies of the same content.
  Pick one container and prove it is the right one (count rows against what you see).
- **Nested tables.** A flat regex ends the outer table at the inner `</table>`.
- **`<br>`-separated values** inside one cell — split explicitly.
- **Client-rendered content.** If the data is not in the HTML you fetched, no regex will
  find it. You need a headless browser; saying so early is the professional answer.
- **Encoding.** `<meta charset>` lies occasionally; watch for mojibake in names.
- **Their terms.** Check `robots.txt` and rate-limit yourself. Scraping is reading; don't
  turn it into an attack.

## Verify against reality

Scraped output should be checked with counts and eyeballed samples: "4 plan rows, matches
the page". A scraper that silently returns 3 of 4 rows is the failure mode you must catch.

Prove it against `drills/004-scrape-table`.

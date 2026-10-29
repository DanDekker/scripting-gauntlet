# The taxonomy of scripting work

Seven families. Most real jobs are a blend of two or three, and the blend tells you which
language to reach for.

---

## 1. data-wrangling

Filter it, join it, aggregate it, reshape it.

| job | canonical move |
| --- | --- |
| filter rows by predicate | `awk '$3 > 100'`, `jq 'select(.ok)'` |
| dedupe / keep-latest | sort by key + timestamp, take last per key |
| group and aggregate | associative arrays (awk), `groupby` (python), `reduce` (jq) |
| join two sources | sort both, `join`, or load one into a dict |
| reshape csv↔json↔tsv | write the smallest converter; don't install one |

**Watch for:** delimiter inside a quoted field, header row that isn't first, duplicate
keys with conflicting values, numbers stored as text with thousands separators.

## 2. api-probing

Hit the thing, page through it, retry it, time it, prove it works.

| job | canonical move |
| --- | --- |
| is it alive | `curl -fsS $BASE/health` then check the body, not the status alone |
| page through results | follow `next` until null, cap iterations, count what you got |
| probe a shape | `curl -s $URL | jq 'keys'` before writing a parser |
| time it | `curl -w '%{time_total}'` — one number, no benchmarking framework |
| auth | header via env var, never the command line (it lands in `ps`) |
| retry | `for i in 1 2 3; do ... && break; sleep $i; done` — that is the whole budget |

**Watch for:** `200` with an error body, pagination that repeats the last page forever,
rate limits that return `200` and an empty list, clocks/timezones in timestamps.

## 3. web-scraping

Pull structure out of markup you do not own.

| job | canonical move |
| --- | --- |
| one table | `html.parser` in python, or a regex anchored on a stable class |
| one field | regex on the smallest unique anchor, not on the whole document |
| saved page, not live | always work from the saved copy first; network is the last variable to add |
| anything JS-rendered | you need a browser; a regex will not do it, and pretending otherwise is the classic failure |

**Watch for:** HTML entities, nested tables, `<br>`-separated values in one cell,
whitespace-only cells, duplicated markup for mobile/desktop.

## 4. file-hygiene

Triage, rename, dedupe, resort a directory full of entropy.

| job | canonical move |
| --- | --- |
| inventory | `find . -type f -printf '%s\t%p\n'` (GNU) or `stat -f` (BSD) |
| dedupe by content | hash everything, group by hash, keep one |
| resort by extension/date | move into `<ext>/` or `<YYYY>/<MM>/` |
| normalize names | lowercase, collapse whitespace to `-`, strip `(1)` and `copy` |
| find junk | zero-byte, `.DS_Store`, `Thumbs.db`, `~$*.docx` |
| dry run | **always** print the plan first; `mv` is not reversible |

**Watch for:** name collisions after normalization, symlinks, case-insensitive
filesystems, files with newlines in the name, permission-bit loss on copy.

## 5. text-munging

Logs, dumps, configs, and output that no one designed for you.

| job | canonical move |
| --- | --- |
| top-N anything | `sort | uniq -c | sort -rn | head -n` |
| extract fields | one regex per line, capture groups, write tab-separated |
| bucket by time | parse to epoch, integer-divide, format back |
| find the anomaly | sort numerically and look at both tails, not just the head |
| normalize | lowercase, strip ANSI, collapse repeated whitespace |

**Watch for:** lines that almost match, multi-line records (stack traces), inode rotation
splitting a record, timestamps without a timezone.

## 6. system-recon

Read host state, identify what matters, and report findings with enough source detail
for someone else to verify them. This is scripting *about* a system, not a systems
programming exercise.

| job | canonical move |
| --- | --- |
| inventory a host | query OS tools and normalize their output |
| triage a process | correlate PID, executable, owner, resources, and open files |
| inspect storage | distinguish device, mount, free space, and deleted-open files |

**Watch for:** platform-specific output, stale process state, permissions, units,
and claims that outrun the evidence you collected.

## 7. network-recon

Inspect local network and protocol facts with bounded, repeatable probes.

| job | canonical move |
| --- | --- |
| inventory listeners | correlate port, protocol, process, and address |
| inspect a response | retain status, headers, timing, and the exact endpoint |
| compare paths | report the concrete difference, not an inferred cause |

**Watch for:** ambiguous hostnames, redirects, retries that hide the first failure,
timeouts mistaken for absence, and accidental calls outside the fixture or
authorized target.

---

## Choosing a language

### bash — the default

Reach for it when the job is **mostly other programs**. If your script is 80% pipes and
20% logic, bash is correct, and python is a mistake that costs you ten minutes and adds
a dependency to your mental load.

Signals you've outgrown it: associative arrays nested two deep, arithmetic that needs
floats, JSON you must actually parse, more than ~100 lines.

### zsh — for the shell you live in

Nothing in a *script* should require zsh. zsh earns its place in interactive work:
globbing (`**/*.png`), parameter expansion (`${(@f)...}`), completion, prompt. Write
`#!/usr/bin/env bash` in scripts; put the zsh tricks in your `.zshrc`. If a script
"needs" zsh, that's a signal to either drop to bash or step up to python.

### python — the escape hatch

Reach for it the moment you need: real data structures, a JSON/YAML document, an HTTP
client with auth, floats and decimal money, or more than a screenful of logic. `python3`
being present is the single most reliable assumption in this book — use it without guilt.

The failure mode is reaching for it *too early* and writing 200 lines where `awk`
wanted 4.

### powershell — objects, and Windows

On Windows it is not optional: registry, WMI/CIM, services, AD, Exchange, Azure. Its
real idea — a pipeline of *objects* rather than text — is genuinely better than text
pipes when the data is structured, and that advantage holds on macOS and Linux too.

Use it when you'd otherwise be parsing `Get-CimInstance` output as text, or when the
target is a Windows box.

### lua — where it's already embedded

You rarely choose lua; lua is already there. nginx/OpenResty, redis scripts, neovim,
wireshark dissectors, game engines, `haproxy`, `awesome`, `mpv`. It is also a fine
choice for tiny footprint config-time transforms where a 200 KB interpreter beats a
40 MB one.

Use it when the host is lua-shaped. Do not use it to write a general CLI — you will
spend your whole timebox on a JSON parser.

The `drills/lua/` track drills the traps that make a lua script wrong where the same
script in another language would be fine: patterns are not regexes, `#` counts bytes and
not characters, `table.sort` is not stable, `ipairs` stops at the first hole, and
`string.format("%q", s)` is Lua escaping rather than JSON.

### JavaScript — browser DOM work

Use the DOM when the task depends on document structure, selectors, or browser
behavior. The `004-scrape-table` reference uses standard DOM APIs; local checks
run them under jsdom so a graphical browser is not needed. Node is the runner,
not the thing that makes the solution browser-specific.

### Perl — dense text and logs

Perl is useful when the job is mostly regex extraction and reporting. The log
triage drill shows that it can parse and rank a noisy access log with only core
modules. Prefer it when Perl is already on the target host.

### Tcl — small host-integrated scripts

Tcl fits tool consoles and embedded interpreters as well as standalone scripts.
Its dictionaries and regular expressions handle the log triage drill without
adding a package dependency. Keep the command/evaluation rules in mind when
building strings from untrusted input.

### JXA — macOS automation

JavaScript for Automation runs through `osascript` and can call macOS Foundation
directly. The plist audit drill uses that native bridge. JXA solutions are
macOS-only; the harness skips them on other operating systems.

---

## Adding coverage

Check `make list` before adding a drill. Name the specific behavior missing
from existing drills, then write a prompt that fully determines the verifier's
judgment. A new variant earns its place by a distinct failure mode or tool
choice, not just a new fixture. See the
[authoring and admission contract](authoring-contract.md) for semantic controls,
source lineage, and evidence stages.

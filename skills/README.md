# skills

Loadable know-how, one pack per family, plus a pack for the Lua language track.
These follow the
[Agent Skills spec](https://agentskills.io/specification): a directory containing
`SKILL.md` with YAML frontmatter, optionally `references/` for detail an agent pulls in
only when it needs it.

| skill | use when | drills |
| --- | --- | --- |
| [`data-wrangling`](data-wrangling/SKILL.md) | counting, grouping, deduping, reshaping CSV/JSON | 001, 006-017, 023-047, 151, 153, 155, 156, 158, 162, 164 |
| [`api-probing`](api-probing/SKILL.md) | poking an HTTP API before trusting it | 003 |
| [`web-scraping`](web-scraping/SKILL.md) | pulling structure out of saved or live markup | 004 |
| [`file-hygiene`](file-hygiene/SKILL.md) | triaging, renaming, deduping, resorting directories | 005, 038, 159, 160 |
| [`text-munging`](text-munging/SKILL.md) | logs, dumps, configs, unstructured output | 002, 014, 018, 150, 152, 154, 157, 161, 163, 165 |
| [`system-recon`](system-recon/SKILL.md) | processes, pids, resources, file descriptors | 048, 049, 052, 053 |
| [`network-recon`](network-recon/SKILL.md) | listeners, sockets, port scans, event logs | 050, 051, 054, 055, 056 |
| [`lua-scripting`](lua-scripting/SKILL.md) | writing standard-library Lua on a Lua-shaped host | 150-160 |
| [`perl-scripting`](perl-scripting/SKILL.md) | writing standard-library Perl on a Perl-shaped host | 161-165 |

A skill is judgement; a drill is proof. If a rule here is worth teaching, there should be
a `verify.py` that fails without it.

Validate the frontmatter after editing:

```bash
make lint     # includes harness/check_skills.py
```

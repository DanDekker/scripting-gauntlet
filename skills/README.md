# skills

Loadable know-how, one pack per family, plus a pack for the Lua language track.
These follow the
[Agent Skills spec](https://agentskills.io/specification): a directory containing
`SKILL.md` with YAML frontmatter, optionally `references/` for detail an agent pulls in
only when it needs it.

| skill | use when | drills |
| --- | --- | --- |
| [`data-wrangling`](data-wrangling/SKILL.md) | counting, grouping, deduping, reshaping CSV/JSON | 001, 006-017, 023-047, 151, 153, 155, 156, 158, 162, 164, 166, 167, 169, 171, 174, 175, 177, 178, 179, 182, 184, 186, 187, 188, 189 |
| [`api-probing`](api-probing/SKILL.md) | poking an HTTP API before trusting it | 003 |
| [`web-scraping`](web-scraping/SKILL.md) | pulling structure out of saved or live markup | 004 |
| [`file-hygiene`](file-hygiene/SKILL.md) | triaging, renaming, deduping, resorting directories | 005, 038, 159, 160 |
| [`text-munging`](text-munging/SKILL.md) | logs, dumps, configs, unstructured output | 002, 014, 018, 150, 152, 154, 157, 161, 163, 165, 168, 170, 172, 173, 176, 180, 181, 183, 185 |
| [`system-recon`](system-recon/SKILL.md) | processes, pids, resources, file descriptors | 048, 049, 052, 053, 190 |
| [`network-recon`](network-recon/SKILL.md) | listeners, sockets, port scans, event logs | 050, 051, 054, 055, 056 |
| [`lua-scripting`](lua-scripting/SKILL.md) | writing standard-library Lua on a Lua-shaped host | 150-160, 171-173, 178-179, 187 |
| [`perl-scripting`](perl-scripting/SKILL.md) | writing standard-library Perl on a Perl-shaped host | 161-165, 174-175, 180-181, 188 |
| [`ruby-scripting`](ruby-scripting/SKILL.md) | writing standard-library Ruby on a Ruby-shaped host | 166-170, 182-183, 189 |
| [`powershell-scripting`](powershell-scripting/SKILL.md) | writing standard-library PowerShell on a PowerShell-shaped host | 176-177, 184-185, 190 |

A skill is judgement; a drill is proof. If a rule here is worth teaching, there should be
a `verify.py` that fails without it.

Validate the frontmatter after editing:

```bash
make lint     # includes harness/check_skills.py
```

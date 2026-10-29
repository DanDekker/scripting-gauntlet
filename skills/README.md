# skills

Loadable know-how, one pack per family. These follow the
[Agent Skills spec](https://agentskills.io/specification): a directory containing
`SKILL.md` with YAML frontmatter, optionally `references/` for detail an agent pulls in
only when it needs it.

| skill | use when | drills |
| --- | --- | --- |
| [`data-wrangling`](data-wrangling/SKILL.md) | counting, grouping, deduping, reshaping CSV/JSON | 001 |
| [`api-probing`](api-probing/SKILL.md) | poking an HTTP API before trusting it | 003 |
| [`web-scraping`](web-scraping/SKILL.md) | pulling structure out of saved or live markup | 004 |
| [`file-hygiene`](file-hygiene/SKILL.md) | triaging, renaming, deduping, resorting directories | 005 |
| [`text-munging`](text-munging/SKILL.md) | logs, dumps, configs, unstructured output | 002 |

A skill is judgement; a drill is proof. If a rule here is worth teaching, there should be
a `verify.py` that fails without it.

Validate the frontmatter after editing:

```bash
make lint     # includes harness/check_skills.py
```

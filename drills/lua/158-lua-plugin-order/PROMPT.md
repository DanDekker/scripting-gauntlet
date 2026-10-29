# 158-lua-plugin-order

> "These plugins declare what they need. Start the ones that can start, in an order that
> works, and tell me which ones can never load instead of hanging the boot."

## Input

`in/plugins.txt` — one plugin per line:

```
auth: store
store:
http: auth, log
```

## Rules

1. A line is `name` or `name: dep, dep`. Blank lines and lines whose first non-whitespace
   character is `#` are ignored.
2. A name and a dep must match `[a-z0-9-]+`. A dep that does not is a **bad-dep** error
   naming that text.
3. A plugin is defined by its **first** line. A later line that reuses a defined name is a
   **duplicate-name** error on that name; the first definition stands and the later line is
   otherwise ignored.
4. A dep that no plugin defines is a **missing-dep** error naming the dep.
5. A plugin that can reach **itself** through its deps is in a **cycle**, and gets a
   `cycle` error. A plugin that depends on itself is a cycle of one.
6. A plugin whose dep has an error is **blocked**, with that dep as detail. This cascades.
   When more than one dep has failed, the detail is the alphabetically smallest of them.
7. **Load order.** Repeatedly take the alphabetically smallest plugin whose deps are all
   already loaded. A plugin with any error is never loaded, and neither is one waiting on
   it.

## Output

Write exactly these files to `$OUT`:

1. **`out/order.csv`** — header `position,name`, one row per loadable plugin in load order,
   `position` counting from 1.
2. **`out/errors.csv`** — header `name,reason`, one row per failed plugin, sorted by `name`
   ascending in byte order. `reason` is one of `bad-dep:<dep>`, `duplicate-name`,
   `missing-dep:<dep>`, `cycle`, `blocked:<dep>`.
3. **`out/summary.json`** — an object with exactly these keys:
   - `plugins` — distinct names defined (int)
   - `loaded` — rows in `order.csv` (int)
   - `failed` — rows in `errors.csv` (int)

   Print it as one compact JSON object: `{"plugins":10,"loaded":5,"failed":5}`.

## Messes to expect

- `mail` needs `smtp`, which nothing defines
- `report` needs `mail`, so it is blocked even though its own line is clean
- `sync` and `sync2` need each other: both are in a cycle and neither can load
- `metrics` is defined twice: that is a duplicate-name error, and the second line is ignored
- the two dependency-free plugins are `log` and `store`, so alphabetical order decides
  which starts first

## Timebox

Five minutes. Fixpoint, then cycles, then topological order with a sorted ready set.

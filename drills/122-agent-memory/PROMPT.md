# 122-agent-memory

> "The agent has been writing observations into a JSONL log all day. Fold them into a
> memory store: newest wins, expire what went stale, and keep it under the cap. I want the
> store and the accounting — how many we dropped and why."

## Input

- `in/memory.jsonl` — one JSON object per line:
  `{"key": "user.name", "value": "Ada", "ts": 1767225600, "ttl": 86400}`
- `in/config.json` — `{"max_entries": 3, "as_of": 1767225600}`

`ts` and `ttl` are epoch seconds (integers). `as_of` is the moment you are folding at.

## Rules

Apply them in this order, tracking each drop separately:

1. **Skip junk** — and do not count it as an observation:
   - blank lines and whitespace-only lines
   - lines that are not valid JSON
   - lines that are valid JSON but not an object
   - entries whose `key` is missing, empty, or not a string

   Every other line is an **observation** (including the ones that turn out to be expired).
2. **Expire.** An entry has a ttl when `ttl` is a non-negative number. It is **expired**
   when `ts + ttl <= as_of` — note `ttl: 0` expires exactly at `as_of`. An expired entry
   is dropped and never reaches the store. A missing (or non-numeric) `ttl` means it
   never expires. A missing (or non-numeric) `ts` is `0`.
3. **Resolve conflicts.** For each key, the surviving entry with the **greatest `ts`**
   wins; when two entries share a key *and* a `ts`, the **later line in the input** wins.
4. **Evict to capacity.** The store holds at most `max_entries` keys. While it is over:
   evict the entry with the **smallest `ts`** (oldest). When several entries share that
   smallest `ts`, evict the one whose **key sorts last** in byte order (`LC_ALL=C`).
   Repeat until the store fits.

The `value` of an entry is its `value` field, unchanged; a missing `value` is the empty
string, and an entry whose value is the empty string is still a real value (it is stored).

## Output

Write exactly these files to `$OUT`:

1. **`out/memory.csv`** — header `key,value,ts`. One row per stored entry, sorted by `ts`
   **descending**, then `key` ascending (byte order). `ts` is written as a plain integer.
2. **`out/summary.json`** — an object with exactly these keys:
   - `observations` — records that survived rule 1, expired ones included (int)
   - `expired` — entries dropped by rule 2 (int)
   - `conflicts` — surviving entries that lost to a newer entry for the same key (int)
   - `stored` — entries in the final store (int)
   - `evicted` — entries dropped by rule 4 (int)
   - `keys` — the keys in the final store, sorted ascending (list of strings)

## Messes to expect

- the same key three times: `user.name` at ts 1767220000, 1767225000 and 1767225000 again —
  the last line wins, and the first two are conflicts
- `deploy.target` written twice with the **same** ts: the later line wins
- `build.branch` with `ttl: 0` (expired, because `ts + 0 <= as_of`) and the same key later
  written with a fresh `ts` and no `ttl` (kept)
- `session.id` with no `ts` at all: it is `0`, so it is the first thing evicted
- an entry with an empty-string value: keep it (`build.branch` survives with an empty
  value, so its CSV row has an empty middle field)
- a blank line, a whitespace-only line, a line of prose, a JSON **array**, and an entry
  with no `key` — five skip cases that must not be counted as observations
- eviction hits a tie: `user.email` and `log.level` both sit at ts 1767223000, and
  `user.email` is evicted because it sorts last

## Timebox

Five minutes. One pass to filter + expire + resolve, then a loop that evicts the minimum
until the store fits; sorting the winners once is enough to pick the evictions.

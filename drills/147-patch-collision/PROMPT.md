# 147-patch-collision

> "Five agents are editing the same repo at once and each one has taken a lease on a line
> range. Tell me which leases are stepping on each other, and give me the smallest number
> of rounds I can run them in without two agents in the same round touching the same
> file."

## Input

`in/leases.csv` — header `agent_id,file,start_line,end_line`, then one lease per row:

```
agent-a,src/app.py,10,25
agent-b,src/app.py,20,35
agent-d,src/utils.py,5,15
```

## Rules

### 1. Which rows are leases

A row is a **valid lease** when, after stripping surrounding whitespace from every field,
it has at least 4 comma-separated fields, `agent_id` and `file` are non-empty, both
`start_line` and `end_line` are plain non-negative integers (digits only — `abc`, `12.5`,
`-3` and an empty field are all invalid), and `1 <= start_line <= end_line`.

Invalid rows are skipped. They still count in `total_leases` (see below), they just produce
no lease.

Duplicate leases — the same `agent_id`, `file`, `start_line` and `end_line` appearing twice
— are **one** lease, not two.

### 2. What counts as a collision

Two leases collide when **all** of:

- they are for the same `file`,
- they are for **different** agents (an agent never collides with itself),
- their ranges overlap inclusively: `max(start_a, start_b) <= min(end_a, end_b)`.

Beware the touching boundary: `[10, 20]` and `[20, 30]` overlap at line 20 and **do**
collide. So do `[1, 100]` and `[100, 120]`.

### 3. Batching (greedy first-fit)

Order the valid leases by `file` ascending, then `start_line` ascending, then `agent_id`
ascending, then `end_line` ascending. Walk that list once, in order, and put each lease in
the **first** batch (1, then 2, then 3 …) that already contains no lease it collides with.
If no existing batch works, open a new one.

## Output

Write exactly these files to `$OUT`:

1. **`out/collisions.csv`** — header `file,agent_1,range_1,agent_2,range_2`. One row per
   colliding pair of leases, with the two agents written so that `agent_1 < agent_2`
   (byte order) and each `range` written `start-end` using the lease's own line numbers.
   Identical rows appear once. Sorted by `file` ascending, then `agent_1` ascending, then
   `agent_2` ascending. (No two leases in this fixture produce the same agent pair twice.)
2. **`out/schedule.csv`** — header `batch,agent_id,file,range`. One row per valid lease.
   Sorted by `batch` numerically ascending, then `file` ascending, then `agent_id`
   ascending. `range` is `start-end`.
3. **`out/summary.json`** — an object with exactly these keys:
   - `total_leases` — every data row of `leases.csv` after the header, blank lines excluded,
     valid or not (int)
   - `valid_leases` — valid leases after dedupe (int)
   - `collision_pairs` — number of rows in `collisions.csv` (int)
   - `total_batches` — number of batches the schedule needed (int)

## Messes to expect

- `agent-g` has `start_line 25 > end_line 10`, `agent-j` is missing a field, `agent-k`
  starts at line 0 and `bad-row` has `abc`: four rows are dropped, so 13 rows are
  `total_leases` but only 8 are `valid_leases`
- `agent-a`'s lease is listed twice: it is one lease, so the schedule has 8 rows, not 9
- `agent-e`'s row is padded with spaces on both sides: trim before comparing
- `lib/db.py` has a *touching* pair, `1-100` and `100-120`: that is a collision, and it
  forces `agent-i` into batch 2
- `src/app.py` gets three collisions but still fits in two batches, because `agent-f`
  (`30-40`) does not collide with `agent-a` (`10-25`)

## Timebox

Four minutes. If you are past that, the approach is wrong.

# 140-agent-loop-detector

> "One of our agents burned 40k tokens yesterday re-reading the same file. I have the
> action log - tell me where it started looping and what the repeating pattern was."

## Input

`in/actions.jsonl` - one JSON object per line, in log order:

```json
{"step": 1, "tool": "read_file", "args": {"path": "src/app.py"}}
```

- `step` - the step counter (number)
- `tool` - the tool that ran (string)
- `args` - an object of arguments; nested objects and arrays may appear, and the raw key
  order is not stable

## Rules

1. **Skip junk.** Blank lines, lines that are not valid JSON, lines that are JSON but not an
   object, and objects without a numeric `step` or a string `tool` are skipped and **not
   counted anywhere**.
2. **Order.** Sort the surviving actions by `step` ascending. Duplicate steps keep input
   order. Everything below uses that sorted sequence.
3. **Action identity.** Two actions are the same action when
   `tool + ":" + compact_normalized_args_json` is equal, where
   `compact_normalized_args_json` is the args object serialized as JSON with **all** object
   keys sorted alphabetically (recursively) and no whitespace, e.g.
   `read_file:{"path":"src/app.py"}`. A missing `args` is `{}`.
4. **Scan greedily, left to right, non-overlapping.** Walk the sorted actions with an index
   `i`, starting at the first action. At each `i`, in this order:

   a. **`repeat_action`** - extend `j` while the action at `j+1` is identical to the action at
      `i`. If `j - i + 1 >= 3`, report `(i, j)` as `repeat_action` and continue at `j+1`.
   b. **`cycle_2`** - extend `j` to the largest index such that every `m` in `[i, j-2]`
      satisfies `action[m] == action[m+2]`. If `j - i + 1 >= 6`, report `(i, j)` as
      `cycle_2` and continue at `j+1`.
   c. **`cycle_3`** - same, with period 3: `action[m] == action[m+3]` for every `m` in
      `[i, j-3]`. If `j - i + 1 >= 6`, report `(i, j)` as `cycle_3` and continue at `j+1`.
   d. Otherwise advance `i` by one.

   Because the scan is greedy and non-overlapping, one long alternating run yields **one**
   row, not one row per offset, and a loop that starts one step after a reported loop is
   not reported separately.
5. `start_step` / `end_step` are the `step` values of the first and last action in the
   reported span (not the indices).
6. `status` is `looping` when at least one row was reported, otherwise `healthy`.

## Output

Write exactly these files to `$OUT`:

1. **`out/loops.csv`** - header `start_step,end_step,pattern_type,description`, one row per
   reported loop, sorted by `start_step` ascending (the scan already emits them in that
   order). `pattern_type` is `repeat_action`, `cycle_2` or `cycle_3`. `description` is:

   | pattern | description |
   | --- | --- |
   | `repeat_action` | `<tool> repeated <n>x` - `n` actions in the run |
   | `cycle_2` | `<tool1> <-> <tool2> x<n>` - `n` = span length / 2 |
   | `cycle_3` | `<tool1> -> <tool2> -> <tool3> x<n>` - `n` = span length / 3 |

   The description names the **tools** of the repeating actions, in order, so a cycle
   between two different arg variants of one tool reads `<tool> <-> <tool>`. No field
   contains a comma, so no quoting.
2. **`out/summary.json`** - an object with exactly these keys:
   - `total_steps` (int) - surviving actions
   - `status` (`"healthy"` or `"looping"`)
   - `loop_count` (int) - rows in `loops.csv`
   - `first_loop_step` (int or `null`) - `start_step` of the first row, `null` when healthy

## Messes to expect

- steps are shuffled and have gaps; sort before you compare anything
- `grep` appears three times with the same args but different raw key order
  (`{"pattern","path"}` vs `{"path","pattern"}`) - it only lines up after normalization
- steps 2, 3, 4 are three `read_file` calls with **different** paths: not a repeat
- steps 30-33 are four identical `run_tests` calls, one of them with its nested `opts` keys
  in a different order: one `repeat_action` of 4, not two of 3
- steps 21-28 ping-pong between two `write_file` arg variants (edit, revert): a period-2
  cycle whose description names the tool twice
- steps 40-47 cycle through three distinct tools: a period-3 cycle
- the file has blank lines, a truncated JSON line, a bare array, and an object with no
  `tool` - four lines that are not actions

## Timebox

Five minutes. If you are past that, the approach is wrong.

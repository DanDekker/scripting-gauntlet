# 227-perl-env-override

> "Our helper scripts started seeing each other's settings. One step set `DRILL_ONE`, and
> the next step's helper read it — the override was meant to last for one command only."

## Input

`in/steps.csv` — header `id,set_var,value,watch_var`:

```csv
id,set_var,value,watch_var
1,DRILL_ONE,alpha,DRILL_ONE
2,DRILL_TWO,beta,DRILL_ONE
3,DRILL_ONE,gamma,DRILL_TWO
4,DRILL_THREE,,DRILL_THREE
```

The `value` column may be empty (row 4).

## Rules

1. The variables named in the fixture are **not** in the environment when the script
   starts.
2. For each step, in file order:
   a. Set `set_var` to `value` **for that step only**. When the step ends, the
      variable must be exactly as it was before the step: absent.
   b. While the override is in effect, run the child
      `perl -e 'print exists $ENV{$ARGV[0]} ? "=$ENV{$ARGV[0]}" : "unset"' <watch_var>`
      and capture its output.
3. Report `seen` for each step — the child's output, verbatim:
   - `=value` when the child saw `watch_var` present, with that value;
   - `unset` when the child did not see it at all.
4. Report `after` for each step — the state of `set_var` in the script's own
   environment once the step has ended, in the same notation: `=value` or `unset`.
5. **`out/steps.csv`** — header `id,set_var,value,watch_var,seen,after`. One row per
   step, in file order. `value` is the fixture's value, verbatim.
6. **`out/summary.json`** — keys `steps`, `seen_set`, `leaked`. One compact JSON object.
   - `steps` — the number of steps.
   - `seen_set` — the number of steps whose child saw the watched variable present.
   - `leaked` — the number of steps after which a variable was still set. This is 0 in
     a correct run.

## Messes to expect

- `$ENV{NAME} = $value` is **global**: it stays set for every later step and every
  later child. `local $ENV{NAME} = $value` scopes it to the enclosing block and puts
  the previous state back when the block ends.
- `local` on a name that was not set before leaves it **absent** afterwards, not set to
  the empty string.
- An empty value is still a value. `$ENV{NAME} = ''` leaves the variable present, and
  the child sees it as present and empty; that is not the same as the variable being
  absent.

## Timebox

Five minutes.

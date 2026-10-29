# Portable awk recipes

Everything here works on POSIX awk (macOS `awk`, `gawk`, `mawk`). Avoid `gensub` (gawk
only) and `PROCINFO` if the script has to run on BSD.

## Setup that prevents most bugs

```awk
BEGIN { FS = OFS = "," }
```

## Strip first and last field of whitespace

```awk
function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
```

`$0` reassignment re-splits the record — always trim into a variable, never in place, if
you still need the other fields.

## CRLF-safe reading

```awk
{ sub(/\r$/, "") }
```

Or, more robustly, strip `\r` inside `trim()` so every field is clean.

## Keep the latest row per key

```awk
{
  id = $1
  if (!(id in ts) || $6 > ts[id]) { ts[id] = $6; line[id] = $0 }
}
END { for (id in line) print line[id] }
```

ISO-8601 UTC timestamps compare correctly as strings. Local time with varying offsets
does not — convert to epoch first.

## Two-key sort without `asort`

```awk
END {
  n = 0; for (k in sum) keys[++n] = k
  for (i = 2; i <= n; i++) {
    v = keys[i]; j = i - 1
    while (j >= 1 && (sum[keys[j]] < sum[v] || (sum[keys[j]] == sum[v] && keys[j] > v))) {
      keys[j+1] = keys[j]; j--
    }
    keys[j+1] = v
  }
  for (i = 1; i <= n; i++) printf "%s,%d,%.2f\n", keys[i], cnt[keys[i]], sum[keys[i]]
}
```

Insertion sort is fine up to a few thousand keys; past that, pipe to `sort` instead.

## Force numeric comparison

```awk
if ($5 + 0 > 1000) ...        # not $5 > 1000 — "9" > "10" as strings
sum[k] += value + 0           # coerce a numeric string once
```

## Name clashes are fatal

In awk a name is **either** a scalar or an array for the whole program. Reusing `code` as
a `split()` target and later as `for (code in arr)` fails with
`can't assign to code; it's an array name`.

## Number formatting

```awk
printf "%.2f\n", x    # rounds; floating point means 0.005 can surprise you
```

For money that must add up exactly, use integer cents in the accumulator and divide once
at print time.

## Debugging without a debugger

```awk
{ print NR ": " NF " fields: " $0 > "/dev/stderr" }
```

`NR` (record number) in the message is the fastest way to find the line that broke your
assumption.

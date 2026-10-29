---
name: powershell-scripting
description: Write throwaway PowerShell that parses CSV/JSON, groups, sorts and emits reports without tripping over pipeline unrolling, case-insensitive comparison, hashtable key folding or decimal formatting. Use when the host is Windows or has pwsh, when the data is already objects (Import-Csv, ConvertFrom-Json), or when existing PowerShell needs its grouping, sorting or money arithmetic checked. Not for cross-platform build tooling or long-lived modules.
license: MIT
metadata:
  family: text-munging
  drill: 176-ps1-group-folding
---

# PowerShell scripting

PowerShell is the shortest path from a CSV to a report on Windows, and it is full of
defaults that are *almost* what you meant. Case-insensitive comparison, case-folding
hashtables, culture-aware sorting and banker's rounding are all choices someone made for
you, and each one quietly changes a report.

## When PowerShell is the right tool

Reach for it when the host is Windows or already has `pwsh`, when the data is structured
(`Import-Csv`, `ConvertFrom-Json` hand you objects with named properties), or when you need
to drive the platform (services, registry, scheduled tasks) from the same script.

Do not reach for it for cross-platform build tooling, or to build a module that outlives
the task.

## The pipeline unrolls everything

```powershell
@(1).Count            # 1
(1).Count             # 1   (PS3+ gives a scalar a Count of 1)
@($null).Count        # 1   an array subexpression keeps the null
@(1,$null,2).Count    # 3
@(1,$null,2) | Measure-Object | Select -Expand Count   # 2 — the null vanished
```

- Emitting a **single-element array** into the pipeline yields the element, not a list.
  `Write-Output -NoEnumerate` (or a leading `,`) keeps it a list.
- `$null` disappears in the pipeline but stays in `@(...)`. A count taken *after* a filter
  is not the count of rows you saw.
- `@(1,2,3) -eq 2` is a **filter** that returns `2`, not a boolean. `-ne` returns the rest.

## Truthiness is not boolean

`$null`, `$false`, `0`, `""` and an empty array are all **false**; everything else,
including `"0"` and `@(0)`, is true. That is closer to Python than to Ruby, and it means a
legitimate `0` needs an explicit `$null -ne $x` test.

## Comparison folds case by default

```powershell
'Hello' -eq 'hello'               # True
@('Hello') -contains 'hello'      # True
'Hello' -ceq 'hello'              # False  — -c prefix is case-sensitive
@('a','A','b') | Group-Object     # a:2, b:1   — folded
@('a','A','b') | Group-Object -CaseSensitive   # a:1, A:1, b:1
```

And the big one: **hashtables fold case too**.

```powershell
$h = @{}; $h['Web'] = 1; $h['web'] = 2; $h.Count   # 1 — same key!
$d = [System.Collections.Generic.Dictionary[string,object]]::new([System.StringComparer]::Ordinal)
```

If case matters, the key type has to say so. `Group-Object -CaseSensitive` is the same
decision one level up.
Drill: `176-ps1-group-folding`.

## Sorting is culture-aware

```powershell
@('b','A','c','B') | Sort-Object                 # A,b,B,c  — culture order
[string]::CompareOrdinal('10','9')               # -8       — byte order
```

`Sort-Object` compares as text in the current culture, so `'10' -lt '9'` is **True**.
Ordinal (byte) order needs `[string]::CompareOrdinal` in a custom comparison, or a sort key
that is already ordinal. This is also why numeric-looking strings sort wrong: convert to
`[int]` first, then sort.

## Money is `[decimal]`, never `[double]`

```powershell
0.1 + 0.2                                  # 0.30000000000000004
[decimal]0.1 + [decimal]0.2                # 0.3
(@(0.1,0.2) | Measure-Object -Sum).Sum     # 0.30000000000000004  — doubles again
[math]::Round(2.5)                         # 2    banker's rounding!
[decimal]::Round([decimal]'1.005', 2)      # 1.00 banker's
[decimal]::Round([decimal]'1.005', 2, [System.MidpointRounding]::AwayFromZero)  # 1.01
([decimal]'1.005').ToString('F2')          # "1.01" after away-from-zero
'{0:F2}' -f 2.675                          # "2.67" — formats the binary double
```

- Parse with `[decimal]::Parse($text, [CultureInfo]::InvariantCulture)`.
- Round with `[decimal]::Round($v, 2, [System.MidpointRounding]::AwayFromZero)`.
- Format with `.ToString('F2', [CultureInfo]::InvariantCulture)`, not `-f`.
- Never accumulate money through `Measure-Object -Sum`.

Drill: `177-ps1-decimal-money`.

## `ConvertTo-Json` truncates at depth 2 by default

```powershell
@{ l1 = @{ l2 = @{ l3 = @{ l4 = @{ l5 = 'deep' } } } } } | ConvertTo-Json -Compress
# {"l1":{"l2":{"l3":"System.Collections.Hashtable"}}}   plus a warning on stream 3
... | ConvertTo-Json -Compress -Depth 10
# full nesting
```

The truncation is silent unless you watch the warning stream — and a string
`"System.Collections.Hashtable"` in your JSON is the tell. Always pass `-Depth`.

`ConvertFrom-Json` returns `PSCustomObject`: a JSON `null` becomes `$null`, a missing key is
absent, and `.PSObject.Properties.Name` tells you which is which. `-AsHashtable` (PS 7)
gives you a dictionary, still subject to the depth limit.

## Errors: set the preference, and check native exit codes

```powershell
$ErrorActionPreference = 'Stop'      # a cmdlet failure throws instead of writing a message
if (-not $env:IN) { throw 'IN not set' }
```

Native commands do **not** throw: `git status` failing sets `$LASTEXITCODE` and writes to
stderr. Check `$LASTEXITCODE` when a native call matters.

Streams: 1 output, 2 error, 3 warning, 4 verbose, 5 debug. `2>$null` hides real errors as
well as noise; prefer `-ErrorAction Stop` and let it fail.

## Emitting CSV

```powershell
$objects | Export-Csv -Path $path -NoTypeInformation -Encoding utf8
```

`Export-Csv` quotes every field and writes a header; `-NoTypeInformation` drops the
`#TYPE` line. Build `[pscustomobject]@{...}` values so the columns are named and ordered.

## Depth 2 is the default

```powershell
@{a=@{b=@{c=@{d=1}}}} | ConvertTo-Json -Compress
# {"a":{"b":{"c":"System.Collections.Hashtable"}}}   plus a warning on stream 3
@{a=@{b=@{c=@{d=1}}}} | ConvertTo-Json -Compress -Depth 10
# full nesting
```

`ConvertTo-Json` truncates anything deeper than 2 by default and replaces the object with
its type name. The warning goes to stream 3, so a run that only watches stream 2 looks
clean. Always pass `-Depth`. `ConvertFrom-Json` has no such limit and returns
`PSCustomObject`: a JSON `null` is `$null`, a missing key is absent, and
`.PSObject.Properties.Name` lists what is actually there.

Drill: `184-ps1-json-depth`.

## Dates are culture and kind

```powershell
[datetime]::Parse('03/04/2026', [cultureinfo]::InvariantCulture)   # March 4
[datetime]::Parse('03/04/2026', [cultureinfo]::GetCultureInfo('en-GB'))  # April 3
[datetime]::ParseExact('03/04/2026', 'dd/MM/yyyy', [cultureinfo]::InvariantCulture)
```

`[datetime]::Parse` decides field order from the culture. When the source format is known,
`ParseExact` with an explicit pattern is the only safe route; an impossible date then
fails instead of rolling forward. `ToUnixTimeSeconds` needs the value marked UTC — use
`[datetime]::SpecifyKind($dt, 'Utc')` or `DateTimeStyles::AdjustToUniversal`, or the epoch
shifts by the local offset. Epoch `0` is a real answer and is falsy.

Drill: `185-ps1-datetime`.

## The four moves

**1. Parse.** `Import-Csv` / `ConvertFrom-Json` / `-split` (a regex). Decide case
sensitivity at the key, not at the comparison.

**2. Validate.** `[decimal]::TryParse`, `[int]::TryParse`, or an anchored `-match`.

**3. Aggregate.** An ordinal `Dictionary[string,object]`, or `Group-Object -CaseSensitive`
when the group name is the key.

**4. Emit.** `Export-Csv -NoTypeInformation` for tables, `ConvertTo-Json -Depth N` for JSON.

## Reporting

Say what you rejected and why, and count the rows you *saw* rather than the rows that
survived a filter. `"4 groups, 6 items, 2 missing"` is checkable.

See [references/powershell-gotchas.md](references/powershell-gotchas.md) for the verified
behaviour tables. Prove it against the `drills/ps/` track: case-folded grouping and decimal
money.

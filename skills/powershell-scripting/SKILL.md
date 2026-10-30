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

## Native binary exit codes and try/catch

```powershell
$ErrorActionPreference = 'Stop'
# Invoking a native binary that exits 42:
$null = my-tool --flag 2>&1
if ($LASTEXITCODE -ne 0) {
    throw "my-tool failed with exit code $LASTEXITCODE"
}
```

`$ErrorActionPreference = 'Stop'` applies to PowerShell cmdlets and terminating script errors.
It does **not** catch non-zero exit codes from native command-line executables (e.g. `git`,
`curl`, `python`, `bash`).
Wrapping a native call in `try { ... } catch { ... }` will silently succeed even when the binary
exits with an error. Always check `$LASTEXITCODE` immediately after native process execution.

Drill: `190-ps1-exitcode-trap`.

## Pipeline unrolling and unary comma

```powershell
function Get-BatchItems($raw) {
    $items = @($raw -split ',' | Where-Object { $_ -ne '' })
    # Prepending comma prevents pipeline flattening of 0- or 1-element arrays:
    return ,$items
}
```

PowerShell's pipeline automatically unrolls collections returned from functions or output blocks.
Returning a single-element array `@("item")` gets flattened into scalar string `"item"`, and returning
`@()` flattens into `$null`.
Downstream code checking array types (`$res -is [array]`) will fail on 1-element and 0-element batches.
The unary comma operator (`,$items`) or `Write-Output -NoEnumerate $items` preserves the collection
envelope through pipeline boundaries.

Drill: `195-ps1-pipeline-unrolling`.

## Regex capture groups and stale $Matches state

```powershell
$pattern = '^LOG (?<id>\d+) status=(?<status>\w+)$'

foreach ($line in $lines) {
    # Crucial: test match condition before reading $Matches!
    if ($line -match $pattern) {
        $id = $Matches['id']
        $status = $Matches['status']
    } else {
        # Do NOT read $Matches! It retains previous line's match values!
        $id = $null
    }
}
```

The `-match` operator sets the `$Matches` automatic variable with full match and named/numbered groups.
However, **if `-match` fails, PowerShell does NOT clear `$Matches`**! It retains whatever values were
matched on the *previous* successful match.
Unconditionally reading `$Matches` inside loops without testing the return value of `-match` causes
corrupt or non-matching records to silently inherit data from earlier lines.

Drill: `200-ps1-regex-groups`.

## Presence is not truthiness

ConvertFrom-Json returns PSCustomObject properties, and a property can be present with
a null value. Test the property collection before reading its value:

~~~powershell
$prop = @($record.PSObject.Properties | Where-Object { $_.Name -ceq 'owner' })
if ($prop.Count -eq 0) {
    $state = 'missing'
} elseif ($null -eq $prop[0].Value) {
    $state = 'null'
} elseif ($prop[0].Value -is [string] -and ([string]$prop[0].Value).Trim() -eq '') {
    $state = 'empty'
} else {
    $state = 'value'
}
~~~

Do not write a truthiness test on the property: it collapses absent, null, empty string,
and numeric zero. A string 0 is a value too. Drill: 241-ps1-json-presence.

## TryParse has two outputs

The Boolean returned by TryParse answers whether parsing succeeded; the [ref] argument
receives the parsed value. Keep them separate so a valid zero does not look like a
failure:

~~~powershell
$value = 0
$ok = [int]::TryParse(
    $text.Trim(),
    [Globalization.NumberStyles]::Integer,
    [Globalization.CultureInfo]::InvariantCulture,
    [ref]$value
)
if ($ok) { ... } else { ... }
~~~

Direct casts are terminating errors for some bad values, but they are not a validation
contract and they make blank/fallback handling easy to get wrong. Drill: 242-ps1-tryparse.

## Let Import-Csv own record boundaries

Import-Csv handles quoted commas, doubled quotes, and a quoted field that spans physical
lines. Get-Content plus split sees physical lines, not CSV records, and will turn one
logical row into two. Keep the imported objects and use Export-Csv for the output.
Drill: 243-ps1-csv-quoted.

## Regex operators are not literal matching

The right side of -match is a regular expression and -match is case-insensitive by
default. If a user rule is literal, escape it and anchor it:

~~~powershell
$pattern = '^{0}$' -f [regex]::Escape($rule.Trim())
$isMatch = $name.Trim() -cmatch $pattern
~~~

String.Equals with StringComparison::Ordinal is another clear choice. Drill:
244-ps1-literal-pattern.

## Encoding and paths are input contracts

PowerShell cannot infer a BOM-less UTF-16LE file. Specify Encoding Unicode when the
source contract says little-endian UTF-16, and specify LiteralPath when a filename can
contain wildcard characters:

~~~powershell
$lines = Get-Content -Encoding Unicode $logPath
$item = Get-Item -LiteralPath $path -Force
$first = Get-Content -LiteralPath $path | Select-Object -First 1
~~~

Encoding is about bytes; LiteralPath is about treating path text as data. Drills:
245-ps1-utf16 and 246-ps1-literal-path.

## Formatting is not serialization

Format-Table and Format-List create display-oriented formatting records. They are not
CSV data and should not be piped into a report file. Build PSCustomObject values with
the exact property order and send those to Export-Csv. Drill: 247-ps1-format-object.

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

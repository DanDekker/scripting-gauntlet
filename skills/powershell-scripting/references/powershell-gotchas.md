# PowerShell gotcha cheat sheet

## Truthiness

| value | truthy? |
| --- | --- |
| `$null` | no |
| `$false` | no |
| `0` | no |
| `""` | no |
| `@()` | no |
| `"0"` | yes |
| `@(0)` | yes |

## Pipeline unrolling

| expression | result |
| --- | --- |
| `@(1).Count` | 1 |
| `(1).Count` | 1 |
| `@($null).Count` | 1 |
| `@(1,$null,2) | Measure-Object` | Count 2 |
| `@(1,2,3) -eq 2` | `2` (filter, not boolean) |
| `@(1,2,3) -eq 9` | empty |
| `,@(1) | Measure-Object` | Count 1 |

## Comparison case

| expression | result |
| --- | --- |
| `'Hello' -eq 'hello'` | True |
| `'Hello' -ceq 'hello'` | False |
| `@('a','A','b') | Group-Object` | a:2, b:1 |
| `... | Group-Object -CaseSensitive` | a:1, A:1, b:1 |
| `$h=@{}; $h['A']=1; $h['a']=2; $h.Count` | 1 |
| ordinal dictionary key | `Dictionary[string,object]::new([StringComparer]::Ordinal)` |

## Sorting

| expression | result |
| --- | --- |
| `@('b','A','c','B') | Sort-Object` | A,b,B,c |
| `'10' -lt '9'` | True |
| `[string]::CompareOrdinal('10','9')` | -8 |
| `@('10','9') | Sort-Object {[int]$_}` | 9,10 |
| numbers as text | convert to `[int]`/`[decimal]` first |

## Numbers and money

| expression | result |
| --- | --- |
| `0.1 + 0.2` | 0.30000000000000004 |
| `[decimal]0.1 + [decimal]0.2` | 0.3 |
| `(@(0.1,0.2) | Measure-Object -Sum).Sum` | 0.30000000000000004 |
| `[math]::Round(2.5)` | 2 (banker's) |
| `[math]::Round(3.5)` | 4 |
| `[decimal]::Round([decimal]'1.005',2)` | 1.00 (banker's) |
| `[decimal]::Round([decimal]'1.005',2,AwayFromZero)` | 1.01 |
| `'{0:F2}' -f 2.675` | 2.67 |
| `([decimal]'1.005').ToString('F2')` | 1.01 |
| `[decimal]'10.10'` | 10.1 (trailing zero is not stored) |
| `([decimal]'10.1').ToString('F2')` | 10.10 |

## JSON

| expression | result |
| --- | --- |
| `@{a=@{b=@{c=1}}} | ConvertTo-Json` | depth 2: `"a":{"b":{...}}` with a warning |
| `... -Depth 10` | full nesting |
| `'{"a":null}' | ConvertFrom-Json` | `.a` is `$null`, key present |
| `.PSObject.Properties.Name` | which keys exist |
| `-AsHashtable` | PS 7+, still depth-limited |

## Strings and splitting

| expression | result |
| --- | --- |
| `'a1b22c' -split '\d+'` | a, b, c (regex) |
| `'a.b'.Split('.')` | a, b (literal char) |
| `"$obj.prop"` | interpolates `$obj`, then literal `.prop` |
| `"$($obj.prop)"` | the property value |
| `-join`, `Join-String` | join an array |

## New track checks

| drill | trap | reliable move |
| --- | --- | --- |
| 241 | missing JSON property, JSON null, empty text, and zero collapse under truthiness | inspect PSObject.Properties, then classify the value |
| 242 | direct casts or fallback zero hide failed integer parsing | use Int32.TryParse(..., [ref]$value) and branch on the Boolean |
| 243 | physical line/comma splitting corrupts quoted CSV | Import-Csv and Export-Csv |
| 244 | -match treats a literal rule as regex and ignores case by default | regex escape, anchors, and -cmatch, or ordinal String.Equals |
| 245 | BOM-less UTF-16LE decodes as NUL-filled text under the default | Get-Content -Encoding Unicode |
| 246 | wildcard characters in a manifest path are reinterpreted | -LiteralPath |
| 247 | Format-Table emits display records, not CSV data | construct objects and Export-Csv |

## Errors

| stream | number |
| --- | --- |
| output | 1 |
| error | 2 |
| warning | 3 |
| verbose | 4 |
| debug | 5 |

`$ErrorActionPreference = 'Stop'` makes cmdlet failures throw. Native commands only set
`$LASTEXITCODE`; check it explicitly.

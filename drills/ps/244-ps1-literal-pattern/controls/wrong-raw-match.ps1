# Plausible bug: -match is regex-based and case-insensitive by default.
$ErrorActionPreference = 'Stop'
$in = $env:IN; $out = $env:OUT
$rows = [System.Collections.Generic.List[object]]::new()
$matched = 0
foreach ($row in Import-Csv (Join-Path $in 'services.csv')) {
    $name = ([string]$row.name).Trim()
    $rule = ([string]$row.rule).Trim()
    $isMatch = $name -match "^$rule$"
    if ($isMatch) { $matched++ }
    $rows.Add([pscustomobject]@{name=$name;rule=$rule;match=if ($isMatch) {'yes'} else {'no'}})
}
$rows | Export-Csv (Join-Path $out 'matches.csv') -NoTypeInformation
@{matched=$matched;unmatched=$rows.Count-$matched} |
    ConvertTo-Json -Compress | Set-Content (Join-Path $out 'summary.json')

# 244-ps1-literal-pattern — escape literal rules before using a regex.
$ErrorActionPreference = 'Stop'
$in = $env:IN; $out = $env:OUT
if (-not $in) { throw 'IN not set' }
if (-not $out) { throw 'OUT not set' }

$rows = [System.Collections.Generic.List[object]]::new()
$matched = 0
foreach ($row in Import-Csv (Join-Path $in 'services.csv')) {
    $name = ([string]$row.name).Trim()
    $rule = ([string]$row.rule).Trim()
    $pattern = '^{0}$' -f [regex]::Escape($rule)
    $isMatch = $name -cmatch $pattern
    if ($isMatch) { $matched++ }
    $rows.Add([pscustomobject][ordered]@{
        name = $name
        rule = $rule
        match = if ($isMatch) { 'yes' } else { 'no' }
    })
}

$rows | Export-Csv -Path (Join-Path $out 'matches.csv') -NoTypeInformation -Encoding utf8
[ordered]@{ matched = $matched; unmatched = $rows.Count - $matched } |
    ConvertTo-Json -Compress | Set-Content -Path (Join-Path $out 'summary.json') -Encoding utf8

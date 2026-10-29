$ErrorActionPreference = 'Stop'
$root = $env:IN
$out = $env:OUT
$sets = @{}
foreach ($name in @('baseline', 'candidate')) {
    $path = Join-Path $root ($name + '.csv')
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "missing input: $path" }
    $groups = @{}
    foreach ($row in Import-Csv -LiteralPath $path) {
        $value = [double]$row.ms
        if ($value -le 0) { throw "non-positive timing for $($row.platform)/$($row.case)" }
        $key = "$($row.platform)|$($row.case)"
        if (-not $groups.ContainsKey($key)) { $groups[$key] = [System.Collections.Generic.List[double]]::new() }
        $groups[$key].Add($value)
    }
    foreach ($key in $groups.Keys) {
        if ($groups[$key].Count -ne 3) { throw "expected three samples for $key in $name.csv" }
    }
    $sets[$name] = $groups
}
$baseKeys = @($sets.baseline.Keys | Sort-Object)
$candidateKeys = @($sets.candidate.Keys | Sort-Object)
if (($baseKeys -join '|') -ne ($candidateKeys -join '|')) { throw 'baseline and candidate pairs differ' }

$rows = foreach ($key in $baseKeys) {
    $before = @($sets.baseline[$key] | Sort-Object)
    $after = @($sets.candidate[$key] | Sort-Object)
    $baseMedian = $before[1]
    $candidateMedian = $after[1]
    $change = [math]::Round(($candidateMedian - $baseMedian) / $baseMedian * 100, 1)
    $parts = $key.Split('|')
    [pscustomobject][ordered]@{
        platform=$parts[0]; case=$parts[1]; baseline_median_ms=$baseMedian
        candidate_median_ms=$candidateMedian; change_pct=$change
        status=$(if ($change -gt 10.0) { 'regression' } else { 'ok' })
    }
}
$rows = @($rows | Sort-Object platform, case)
$rows | Export-Csv -LiteralPath (Join-Path $out 'comparison.csv') -NoTypeInformation -Encoding utf8
$regressions = @($rows | Where-Object status -eq 'regression').Count
[ordered]@{ comparisons=$rows.Count; regressions=$regressions; threshold_pct=10 } |
    ConvertTo-Json -Compress | Set-Content -LiteralPath (Join-Path $out 'summary.json') -Encoding utf8

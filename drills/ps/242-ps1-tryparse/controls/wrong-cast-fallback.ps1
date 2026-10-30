# Plausible bug: direct casts and a fallback value turn blank input into a fake zero.
$ErrorActionPreference = 'Stop'
$in = $env:IN; $out = $env:OUT
$rows = [System.Collections.Generic.List[object]]::new()
$rejected = 0
$total = 0
foreach ($row in Import-Csv (Join-Path $in 'measurements.csv')) {
    try {
        $value = [int]$row.raw
    }
    catch {
        $value = 0
    }
    $rows.Add([pscustomobject]@{name=$row.name;value=$value})
    $total += $value
}
$rows | Export-Csv (Join-Path $out 'readings.csv') -NoTypeInformation
@{accepted=$rows.Count;rejected=$rejected;total=$total} |
    ConvertTo-Json -Compress | Set-Content (Join-Path $out 'summary.json')

# 242-ps1-tryparse — the Boolean result and the [ref] value are separate.
$ErrorActionPreference = 'Stop'
$in = $env:IN; $out = $env:OUT
if (-not $in) { throw 'IN not set' }
if (-not $out) { throw 'OUT not set' }

$rows = [System.Collections.Generic.List[object]]::new()
$rejected = 0
$total = 0
$culture = [System.Globalization.CultureInfo]::InvariantCulture
$styles = [System.Globalization.NumberStyles]::Integer

foreach ($row in Import-Csv (Join-Path $in 'measurements.csv')) {
    $text = ([string]$row.raw).Trim()
    $value = 0
    if ([int]::TryParse($text, $styles, $culture, [ref]$value)) {
        $rows.Add([pscustomobject][ordered]@{ name = $row.name; value = $value })
        $total += $value
    }
    else {
        $rejected++
    }
}

$rows | Export-Csv -Path (Join-Path $out 'readings.csv') -NoTypeInformation -Encoding utf8
[ordered]@{ accepted = $rows.Count; rejected = $rejected; total = $total } |
    ConvertTo-Json -Compress | Set-Content -Path (Join-Path $out 'summary.json') -Encoding utf8

# Plausible bug: wildcard-aware path parameters reinterpret the manifest data.
$ErrorActionPreference = 'Stop'
$in = $env:IN; $out = $env:OUT
$root = Join-Path $in 'tree'
$rows = [System.Collections.Generic.List[object]]::new()
$bytes = 0
foreach ($entry in Import-Csv (Join-Path $in 'manifest.csv')) {
    $relative = $entry.path.Trim()
    $path = Join-Path $root $relative
    $item = Get-Item $path -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $item) { continue }
    $firstLine = (Get-Content $path | Select-Object -First 1).Trim()
    $rows.Add([pscustomobject]@{path=$relative;bytes=$item.Length;first_line=$firstLine})
    $bytes += $item.Length
}
$rows | Export-Csv (Join-Path $out 'inventory.csv') -NoTypeInformation
@{files=$rows.Count;bytes=$bytes} |
    ConvertTo-Json -Compress | Set-Content (Join-Path $out 'summary.json')

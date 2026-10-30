# 246-ps1-literal-path — manifest paths are data, so use LiteralPath.
$ErrorActionPreference = 'Stop'
$in = $env:IN; $out = $env:OUT
if (-not $in) { throw 'IN not set' }
if (-not $out) { throw 'OUT not set' }

$root = Join-Path $in 'tree'
$rows = [System.Collections.Generic.List[object]]::new()
$bytes = 0
foreach ($entry in Import-Csv (Join-Path $in 'manifest.csv')) {
    $relative = ([string]$entry.path).Trim()
    $path = Join-Path $root $relative
    $item = Get-Item -LiteralPath $path -Force
    $firstLine = (Get-Content -LiteralPath $path | Select-Object -First 1).Trim()
    $rows.Add([pscustomobject][ordered]@{
        path = $relative
        bytes = [long]$item.Length
        first_line = $firstLine
    })
    $bytes += $item.Length
}

$rows | Export-Csv -Path (Join-Path $out 'inventory.csv') -NoTypeInformation -Encoding utf8
[ordered]@{ files = $rows.Count; bytes = $bytes } |
    ConvertTo-Json -Compress | Set-Content -Path (Join-Path $out 'summary.json') -Encoding utf8

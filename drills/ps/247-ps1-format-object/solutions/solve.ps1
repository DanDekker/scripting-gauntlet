# 247-ps1-format-object — keep objects until the data serializer.
$ErrorActionPreference = 'Stop'
$in = $env:IN; $out = $env:OUT
if (-not $in) { throw 'IN not set' }
if (-not $out) { throw 'OUT not set' }

$rows = [System.Collections.Generic.List[object]]::new()
$healthy = 0
$down = 0
$slow = 0
foreach ($row in Import-Csv (Join-Path $in 'services.csv')) {
    $latency = [int]$row.latency_ms
    $isHealthy = $row.status -ceq 'up' -and $latency -le 100
    if ($isHealthy) { $healthy++ }
    if ($row.status -ceq 'down') { $down++ }
    if ($latency -gt 100) { $slow++ }
    $rows.Add([pscustomobject][ordered]@{
        name = $row.name
        status = $row.status
        latency_ms = $latency
        owner = $row.owner
        healthy = if ($isHealthy) { 'yes' } else { 'no' }
    })
}

$rows | Export-Csv -Path (Join-Path $out 'report.csv') -NoTypeInformation -Encoding utf8
[ordered]@{services=$rows.Count;healthy=$healthy;down=$down;slow=$slow} |
    ConvertTo-Json -Compress | Set-Content -Path (Join-Path $out 'summary.json') -Encoding utf8

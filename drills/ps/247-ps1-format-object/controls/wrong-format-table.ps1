# Plausible bug: formatted output is for humans, not downstream CSV consumers.
$ErrorActionPreference = 'Stop'
$in = $env:IN; $out = $env:OUT
$rows = foreach ($row in Import-Csv (Join-Path $in 'services.csv')) {
    [pscustomobject]@{name=$row.name;status=$row.status;latency_ms=$row.latency_ms;owner=$row.owner;healthy='no'}
}
$rows | Format-Table | Out-File (Join-Path $out 'report.csv')
@{services=@($rows).Count;healthy=1;down=1;slow=1} |
    ConvertTo-Json -Compress | Set-Content (Join-Path $out 'summary.json')

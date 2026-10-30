# 245-ps1-utf16 — Unicode is UTF-16LE in PowerShell's encoding aliases.
$ErrorActionPreference = 'Stop'
$in = $env:IN; $out = $env:OUT
if (-not $in) { throw 'IN not set' }
if (-not $out) { throw 'OUT not set' }

$rows = [System.Collections.Generic.List[object]]::new()
$counts = @{ INFO = 0; WARN = 0; ERROR = 0 }
foreach ($line in Get-Content -Encoding Unicode (Join-Path $in 'events.log')) {
    $text = ([string]$line).Trim()
    if (-not $text) { continue }
    $fields = $text.Split('|', 2)
    if ($fields.Count -ne 2) { throw "malformed event: $line" }
    $level = $fields[0].Trim()
    $message = $fields[1].Trim()
    if (-not $counts.ContainsKey($level)) { throw "unknown level: $level" }
    $counts[$level]++
    $rows.Add([pscustomobject][ordered]@{ level = $level; message = $message })
}

$rows | Export-Csv -Path (Join-Path $out 'events.csv') -NoTypeInformation -Encoding utf8
[ordered]@{
    records = $rows.Count
    info = $counts.INFO
    warn = $counts.WARN
    error = $counts.ERROR
} | ConvertTo-Json -Compress | Set-Content -Path (Join-Path $out 'summary.json') -Encoding utf8

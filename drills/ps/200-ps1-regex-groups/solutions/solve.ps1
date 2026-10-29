# 200-ps1-regex-groups — guard -match to prevent stale $Matches leakage
$ErrorActionPreference = 'Stop'
$in = $env:IN; $out = $env:OUT
if (-not $in) { throw 'IN not set' }
if (-not $out) { throw 'OUT not set' }

$pattern = '^LOG (?<stamp>\S+) ID=(?<id>\d+) status=(?<status>\w+) duration_ms=(?<dur>\d+)$'
$lines = Get-Content (Join-Path $in 'events.log')

$results = [System.Collections.Generic.List[object]]::new()
$step = 0
$validCount = 0
$corruptCount = 0
$totalDuration = 0

foreach ($line in $lines) {
    $trimmed = $line.Trim()
    if (-not $trimmed -or $trimmed.StartsWith('#')) { continue }

    $step++
    # Crucial: test match condition to avoid reading stale $Matches
    if ($trimmed -match $pattern) {
        $validCount++
        $id = [int]$Matches['id']
        $status = [string]$Matches['status']
        $dur = [int]$Matches['dur']
        $totalDuration += $dur
        $valid = 'true'
    } else {
        $corruptCount++
        $id = ''
        $status = ''
        $dur = ''
        $valid = 'false'
    }

    $results.Add([pscustomobject]@{
        step     = $step
        id       = $id
        status   = $status
        duration = $dur
        valid    = $valid
    })
}

$results | Export-Csv -Path (Join-Path $out 'parsed.csv') -NoTypeInformation -Encoding utf8

$avgDur = if ($validCount -gt 0) { [int]($totalDuration / $validCount) } else { 0 }
@{
    total_lines   = $results.Count
    valid_records = $validCount
    corrupt_lines = $corruptCount
    avg_duration  = $avgDur
} | ConvertTo-Json -Compress | Set-Content -Path (Join-Path $out 'summary.json') -Encoding utf8

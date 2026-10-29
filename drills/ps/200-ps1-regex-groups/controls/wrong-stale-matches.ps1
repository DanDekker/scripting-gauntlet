# Plausible bug: unconditionally reads $Matches without checking -match return value
$ErrorActionPreference = 'Stop'
$in = $env:IN; $out = $env:OUT
if (-not $in) { throw 'IN not set' }
if (-not $out) { throw 'OUT not set' }

$pattern = '^LOG (?<stamp>\S+) ID=(?<id>\d+) status=(?<status>\w+) duration_ms=(?<dur>\d+)$'
$lines = Get-Content (Join-Path $in 'events.log')

$results = [System.Collections.Generic.List[object]]::new()
$step = 0
$totalDuration = 0

foreach ($line in $lines) {
    $trimmed = $line.Trim()
    if (-not $trimmed -or $trimmed.StartsWith('#')) { continue }

    $step++
    # BUG: executes -match without testing result; $Matches retains prior values on failure!
    $null = $trimmed -match $pattern

    $id = [int]$Matches['id']
    $status = [string]$Matches['status']
    $dur = [int]$Matches['dur']
    $totalDuration += $dur
    $valid = 'true'

    $results.Add([pscustomobject]@{
        step     = $step
        id       = $id
        status   = $status
        duration = $dur
        valid    = $valid
    })
}

$results | Export-Csv -Path (Join-Path $out 'parsed.csv') -NoTypeInformation -Encoding utf8

@{
    total_lines   = $results.Count
    valid_records = $results.Count
    corrupt_lines = 0
    avg_duration  = [int]($totalDuration / $results.Count)
} | ConvertTo-Json -Compress | Set-Content -Path (Join-Path $out 'summary.json') -Encoding utf8

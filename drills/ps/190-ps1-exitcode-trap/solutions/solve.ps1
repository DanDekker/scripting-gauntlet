# 190-ps1-exitcode-trap — native process execution and LASTEXITCODE inspection
$ErrorActionPreference = 'Stop'
$in = $env:IN; $out = $env:OUT
if (-not $in) { throw 'IN not set' }
if (-not $out) { throw 'OUT not set' }

$steps = Import-Csv (Join-Path $in 'steps.csv')
$results = [System.Collections.Generic.List[object]]::new()
$succeeded = 0
$failed = 0

foreach ($step in $steps) {
    $targetCode = [int]$step.code
    # Run native binary
    $null = python3 -c "import sys; sys.exit(int(sys.argv[1]))" $targetCode 2>&1
    $actualCode = $LASTEXITCODE

    $status = if ($actualCode -eq 0) {
        $succeeded++
        'success'
    } else {
        $failed++
        'failed'
    }

    $results.Add([pscustomobject]@{
        id     = [int]$step.id
        action = [string]$step.action
        code   = [int]$actualCode
        status = [string]$status
    })
}

$results | Export-Csv -Path (Join-Path $out 'results.csv') -NoTypeInformation -Encoding utf8

@{
    total_steps = $results.Count
    succeeded   = $succeeded
    failed      = $failed
} | ConvertTo-Json -Compress | Set-Content -Path (Join-Path $out 'summary.json') -Encoding utf8

# 195-ps1-pipeline-unrolling — unary comma operator prevents pipeline array flattening
$ErrorActionPreference = 'Stop'
$in = $env:IN; $out = $env:OUT
if (-not $in) { throw 'IN not set' }
if (-not $out) { throw 'OUT not set' }

function Get-BatchItems($rawItems) {
    if ([string]::IsNullOrWhiteSpace($rawItems)) {
        # Return empty array wrapped with unary comma
        return ,@()
    }
    $items = @($rawItems -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' })
    # Unary comma prevents PowerShell from unrolling single-element arrays
    return ,$items
}

$lines = Get-Content (Join-Path $in 'batches.txt')
$results = [System.Collections.Generic.List[object]]::new()
$totalItems = 0
$singleBatches = 0
$emptyBatches = 0

foreach ($line in $lines) {
    $trimmed = $line.Trim()
    if (-not $trimmed -or $trimmed.StartsWith('#')) { continue }

    $parts = $trimmed -split ':', 2
    $id = [int]$parts[0]
    $rawItems = if ($parts.Length -gt 1) { $parts[1] } else { '' }

    $batch = Get-BatchItems $rawItems
    $isArray = if ($batch -is [array]) { 'true' } else { 'false' }
    $count = if ($batch -is [array]) { $batch.Length } else { 1 }
    $first = if ($count -gt 0) { $batch[0] } else { '' }

    $totalItems += $count
    if ($count -eq 1) { $singleBatches++ }
    if ($count -eq 0) { $emptyBatches++ }

    $results.Add([pscustomobject]@{
        id       = $id
        count    = $count
        is_array = $isArray
        first    = $first
    })
}

$results | Export-Csv -Path (Join-Path $out 'batches.csv') -NoTypeInformation -Encoding utf8

@{
    batches             = $results.Count
    total_items         = $totalItems
    single_item_batches = $singleBatches
    empty_batches       = $emptyBatches
} | ConvertTo-Json -Compress | Set-Content -Path (Join-Path $out 'summary.json') -Encoding utf8

# 176-ps1-group-folding — case-sensitive grouping, ordinal order, every row counted.
$ErrorActionPreference = 'Stop'
$in = $env:IN; $out = $env:OUT
if (-not $in) { throw 'IN not set' }
if (-not $out) { throw 'OUT not set' }

$rows = Import-Csv (Join-Path $in 'items.csv')
$buckets = [System.Collections.Generic.Dictionary[string, object]]::new([System.StringComparer]::Ordinal)

foreach ($row in $rows) {
    $key = [string]$row.group
    if (-not $buckets.ContainsKey($key)) {
        $buckets[$key] = [pscustomobject]@{ group = $key; count = 0; total = [decimal]0; missing = 0 }
    }
    $bucket = $buckets[$key]
    $bucket.count++
    if ([string]::IsNullOrWhiteSpace([string]$row.amount)) {
        $bucket.missing++
    }
    else {
        $parsed = [decimal]0
        if (-not [decimal]::TryParse(([string]$row.amount), [ref]$parsed)) {
            throw "items.csv: id $($row.id): amount is not a number: '$($row.amount)'"
        }
        $bucket.total += $parsed
    }
}

$ordered = [System.Collections.Generic.List[object]]::new()
foreach ($bucket in $buckets.Values) { $ordered.Add($bucket) }
$ordered.Sort([System.Comparison[object]] { param($a, $b) [string]::CompareOrdinal($a.group, $b.group) })

$ordered | Export-Csv -Path (Join-Path $out 'groups.csv') -NoTypeInformation -Encoding utf8

$missing = 0
foreach ($bucket in $ordered) { $missing += $bucket.missing }
@{
    groups  = $ordered.Count
    items   = $rows.Count
    missing = $missing
} | ConvertTo-Json -Compress | Set-Content -Path (Join-Path $out 'summary.json') -Encoding utf8

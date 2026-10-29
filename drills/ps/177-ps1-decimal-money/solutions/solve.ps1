# 177-ps1-decimal-money — decimal accumulation, away-from-zero rounding, F2 formatting.
$ErrorActionPreference = 'Stop'
$in = $env:IN; $out = $env:OUT
if (-not $in) { throw 'IN not set' }
if (-not $out) { throw 'OUT not set' }

$rows = Import-Csv (Join-Path $in 'amounts.csv')
$sums = [ordered]@{}
$counts = @{}
$half = @{}

foreach ($row in $rows) {
    $account = [string]$row.account
    $value = [decimal]::Parse(([string]$row.amount).Trim(), [System.Globalization.CultureInfo]::InvariantCulture)
    if (-not $sums.Contains($account)) { $sums[$account] = [decimal]0; $counts[$account] = 0 }
    $sums[$account] += $value
    $counts[$account]++
}

$records = foreach ($account in $sums.Keys) {
    $exact = $sums[$account]
    $rounded = [decimal]::Round($exact, 2, [System.MidpointRounding]::AwayFromZero)
    $third = [math]::Abs(($exact * 1000) % 10)
    [pscustomobject]@{
        account = $account
        total   = $rounded.ToString('F2', [System.Globalization.CultureInfo]::InvariantCulture)
        items   = $counts[$account]
        half    = ($third -eq 5)
    }
}

$ordered = [System.Collections.Generic.List[object]]::new()
foreach ($record in $records) { $ordered.Add($record) }
$ordered.Sort([System.Comparison[object]] { param($a, $b) [string]::CompareOrdinal($a.account, $b.account) })

$rowsOut = $ordered | Select-Object account, total, items
$rowsOut | Export-Csv -Path (Join-Path $out 'totals.csv') -NoTypeInformation -Encoding utf8

$grand = [decimal]0
$halfCount = 0
foreach ($record in $ordered) {
    $grand += [decimal]::Parse($record.total, [System.Globalization.CultureInfo]::InvariantCulture)
    if ($record.half) { $halfCount++ }
}
$grandRounded = [decimal]::Round($grand, 2, [System.MidpointRounding]::AwayFromZero)
@{
    accounts   = $ordered.Count
    total      = $grandRounded.ToString('F2', [System.Globalization.CultureInfo]::InvariantCulture)
    half_cents = $halfCount
} | ConvertTo-Json -Compress | Set-Content -Path (Join-Path $out 'summary.json') -Encoding utf8

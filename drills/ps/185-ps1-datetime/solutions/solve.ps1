# 185-ps1-datetime — explicit patterns, day-first for the European feed, UTC for the epoch.
$ErrorActionPreference = 'Stop'
$in = $env:IN; $out = $env:OUT
if (-not $in) { throw 'IN not set' }
if (-not $out) { throw 'OUT not set' }

$culture = [System.Globalization.CultureInfo]::InvariantCulture
$records = Import-Csv (Join-Path $in 'stamps.csv')
$rows = [System.Collections.Generic.List[object]]::new()
$invalid = 0

foreach ($record in $records) {
    $stamp = ([string]$record.stamp).Trim()
    $epoch = $null
    try {
        $moment = [datetime]::ParseExact(
            $stamp, 'yyyy-MM-ddTHH:mm:ssZ', $culture,
            [System.Globalization.DateTimeStyles]::AdjustToUniversal)
        $epoch = [datetimeoffset]::new([datetime]::SpecifyKind($moment, 'Utc')).ToUnixTimeSeconds()
    }
    catch {
        try {
            # the European feed: day first, midnight UTC
            $moment = [datetime]::ParseExact($stamp, 'dd/MM/yyyy', $culture)
            $epoch = [datetimeoffset]::new([datetime]::SpecifyKind($moment, 'Utc')).ToUnixTimeSeconds()
        }
        catch {
            $invalid++
        }
    }
    if ($null -ne $epoch) {
        $rows.Add([pscustomobject]@{ id = [int]$record.id; epoch = [long]$epoch })
    }
}

$ordered = [System.Collections.Generic.List[object]]::new()
foreach ($row in $rows) { $ordered.Add($row) }
$ordered.Sort([System.Comparison[object]] { param($a, $b) $a.id.CompareTo($b.id) })
$ordered | Export-Csv -Path (Join-Path $out 'epochs.csv') -NoTypeInformation -Encoding utf8

$earliest = if ($ordered.Count -gt 0) { ($ordered | Measure-Object -Property epoch -Minimum).Minimum } else { '' }
@{ rows = $ordered.Count; invalid = $invalid; earliest = $earliest } |
    ConvertTo-Json -Compress | Set-Content -Path (Join-Path $out 'summary.json') -Encoding utf8

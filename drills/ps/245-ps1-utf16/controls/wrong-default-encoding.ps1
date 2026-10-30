# Plausible bug: no encoding is specified for a BOM-less UTF-16LE file.
$ErrorActionPreference = 'Stop'
$in = $env:IN; $out = $env:OUT
$rows = foreach ($line in Get-Content (Join-Path $in 'events.log')) {
    if (-not $line.Trim()) { continue }
    $fields = $line -split '\|', 2
    if ($fields.Count -eq 2) {
        [pscustomobject]@{level=$fields[0].Trim();message=$fields[1].Trim()}
    }
}
$rows | Export-Csv (Join-Path $out 'events.csv') -NoTypeInformation
@{records=@($rows).Count;info=0;warn=0;error=0} |
    ConvertTo-Json -Compress | Set-Content (Join-Path $out 'summary.json')

# Plausible bug: physical lines are not CSV records when a field contains a newline.
$ErrorActionPreference = 'Stop'
$in = $env:IN; $out = $env:OUT
$rows = [System.Collections.Generic.List[object]]::new()
foreach ($line in Get-Content (Join-Path $in 'invoices.csv') | Select-Object -Skip 1) {
    $fields = $line -split ','
    if ($fields.Count -lt 5) { continue }
    $rows.Add([pscustomobject]@{
        order_id = $fields[0]
        customer = $fields[1].Trim('"')
        units = $fields[3]
        unit_price = $fields[4]
        total = $fields[3]
    })
}
$rows | Export-Csv (Join-Path $out 'invoices.csv') -NoTypeInformation
@{orders=$rows.Count;grand_total=0;zero_quantity=0} |
    ConvertTo-Json -Compress | Set-Content (Join-Path $out 'summary.json')

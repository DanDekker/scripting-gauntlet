# 243-ps1-csv-quoted — let Import-Csv own the record boundaries.
$ErrorActionPreference = 'Stop'
$in = $env:IN; $out = $env:OUT
if (-not $in) { throw 'IN not set' }
if (-not $out) { throw 'OUT not set' }

$culture = [System.Globalization.CultureInfo]::InvariantCulture
$rows = [System.Collections.Generic.List[object]]::new()
$grandTotal = [decimal]0
$zeroQuantity = 0

foreach ($row in Import-Csv (Join-Path $in 'invoices.csv')) {
    $units = [int]::Parse($row.units, $culture)
    $unitPrice = [decimal]::Parse($row.unit_price, $culture)
    $total = [decimal]::Round($units * $unitPrice, 2, [System.MidpointRounding]::AwayFromZero)
    if ($units -eq 0) { $zeroQuantity++ }
    $grandTotal += $total
    $rows.Add([pscustomobject][ordered]@{
        order_id = $row.order_id
        customer = $row.customer
        units = $units
        unit_price = $unitPrice.ToString('F2', $culture)
        total = $total.ToString('F2', $culture)
    })
}

$rows | Export-Csv -Path (Join-Path $out 'invoices.csv') -NoTypeInformation -Encoding utf8
[ordered]@{
    orders = $rows.Count
    grand_total = [decimal]::Round($grandTotal, 2, [System.MidpointRounding]::AwayFromZero)
    zero_quantity = $zeroQuantity
} | ConvertTo-Json -Compress | Set-Content -Path (Join-Path $out 'summary.json') -Encoding utf8

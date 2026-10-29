# Plausible bug: serialises the echo with the default depth of 2.
$ErrorActionPreference = 'Stop'
$in = $env:IN; $out = $env:OUT
if (-not $in) { throw 'IN not set' }
if (-not $out) { throw 'OUT not set' }

$config = Get-Content -Raw -Path (Join-Path $in 'config.json') | ConvertFrom-Json
$rows = [System.Collections.Generic.List[object]]::new()

function Add-FlatRows($value, $prefix) {
    if ($null -eq $value) {
        $rows.Add([pscustomobject]@{ key = $prefix; type = 'null'; value = '' })
    }
    elseif ($value -is [bool]) {
        $text = if ($value) { 'true' } else { 'false' }
        $rows.Add([pscustomobject]@{ key = $prefix; type = 'bool'; value = $text })
    }
    elseif ($value -is [int] -or $value -is [long]) {
        $rows.Add([pscustomobject]@{ key = $prefix; type = 'int'; value = "$value" })
    }
    elseif ($value -is [array]) {
        $rows.Add([pscustomobject]@{ key = $prefix; type = 'array'; value = ($value -join '|') })
    }
    elseif ($value -is [System.Management.Automation.PSCustomObject]) {
        foreach ($property in $value.PSObject.Properties) {
            $child = if ($prefix) { "$prefix.$($property.Name)" } else { $property.Name }
            Add-FlatRows $property.Value $child
        }
    }
    else {
        $rows.Add([pscustomobject]@{ key = $prefix; type = 'string'; value = "$value" })
    }
}

Add-FlatRows $config ''

$ordered = [System.Collections.Generic.List[object]]::new()
foreach ($row in $rows) { $ordered.Add($row) }
$ordered.Sort([System.Comparison[object]] { param($a, $b) [string]::CompareOrdinal($a.key, $b.key) })
$ordered | Export-Csv -Path (Join-Path $out 'flat.csv') -NoTypeInformation -Encoding utf8

# -Depth is the whole point: the default of 2 rewrites deep objects as a type name
$config | ConvertTo-Json | Set-Content -Path (Join-Path $out 'echo.json') -Encoding utf8

@{
    keys   = $ordered.Count
    nulls  = @($ordered | Where-Object { $_.type -eq 'null' }).Count
    arrays = @($ordered | Where-Object { $_.type -eq 'array' }).Count
} | ConvertTo-Json -Compress | Set-Content -Path (Join-Path $out 'summary.json') -Encoding utf8

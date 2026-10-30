# 241-ps1-json-presence — inspect property presence before testing values.
$ErrorActionPreference = 'Stop'
$in = $env:IN; $out = $env:OUT
if (-not $in) { throw 'IN not set' }
if (-not $out) { throw 'OUT not set' }

$records = @(Get-Content -Raw (Join-Path $in 'records.json') | ConvertFrom-Json)
$rows = [System.Collections.Generic.List[object]]::new()
$summary = [ordered]@{
    records = $records.Count
    owner_missing = 0
    owner_null = 0
    owner_empty = 0
    quota_missing = 0
    quota_null = 0
}

foreach ($record in $records) {
    $ownerProperty = @($record.PSObject.Properties | Where-Object { $_.Name -ceq 'owner' })
    if ($ownerProperty.Count -eq 0) {
        $ownerState = 'missing'
        $ownerValue = ''
        $summary.owner_missing++
    }
    elseif ($null -eq $ownerProperty[0].Value) {
        $ownerState = 'null'
        $ownerValue = ''
        $summary.owner_null++
    }
    elseif ($ownerProperty[0].Value -is [string] -and
            ([string]$ownerProperty[0].Value).Trim().Length -eq 0) {
        $ownerState = 'empty'
        $ownerValue = ''
        $summary.owner_empty++
    }
    else {
        $ownerState = 'value'
        $ownerValue = if ($ownerProperty[0].Value -is [string]) {
            ([string]$ownerProperty[0].Value).Trim()
        } else {
            [string]$ownerProperty[0].Value
        }
    }

    $quotaProperty = @($record.PSObject.Properties | Where-Object { $_.Name -ceq 'quota' })
    if ($quotaProperty.Count -eq 0) {
        $quotaState = 'missing'
        $quotaValue = ''
        $summary.quota_missing++
    }
    elseif ($null -eq $quotaProperty[0].Value) {
        $quotaState = 'null'
        $quotaValue = ''
        $summary.quota_null++
    }
    else {
        $quota = [long]$quotaProperty[0].Value
        $quotaState = if ($quota -eq 0) { 'zero' } elseif ($quota -gt 0) { 'positive' } else { 'negative' }
        $quotaValue = $quota
    }

    $rows.Add([pscustomobject][ordered]@{
        id = ([string]$record.id).Trim()
        owner_state = $ownerState
        owner_value = $ownerValue
        quota_state = $quotaState
        quota_value = $quotaValue
    })
}

$rows | Export-Csv -Path (Join-Path $out 'report.csv') -NoTypeInformation -Encoding utf8
$summary | ConvertTo-Json -Compress | Set-Content -Path (Join-Path $out 'summary.json') -Encoding utf8

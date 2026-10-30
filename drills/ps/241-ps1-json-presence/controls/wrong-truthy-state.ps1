# Plausible bug: a truthiness test cannot distinguish missing, null, empty, or zero.
$ErrorActionPreference = 'Stop'
$in = $env:IN; $out = $env:OUT
$records = @(Get-Content -Raw (Join-Path $in 'records.json') | ConvertFrom-Json)
$rows = foreach ($record in $records) {
    if ($record.owner) { $ownerState = 'value'; $ownerValue = [string]$record.owner }
    else { $ownerState = 'empty'; $ownerValue = '' }
    if ($record.quota) { $quotaState = if ($record.quota -gt 0) { 'positive' } else { 'negative' }; $quotaValue = $record.quota }
    else { $quotaState = 'zero'; $quotaValue = '' }
    [pscustomobject]@{
        id = $record.id
        owner_state = $ownerState
        owner_value = $ownerValue
        quota_state = $quotaState
        quota_value = $quotaValue
    }
}
$rows | Export-Csv (Join-Path $out 'report.csv') -NoTypeInformation
@{records=$records.Count;owner_missing=0;owner_null=0;owner_empty=0;quota_missing=0;quota_null=0} |
    ConvertTo-Json -Compress | Set-Content (Join-Path $out 'summary.json')

$ErrorActionPreference = 'Stop'
$root = $env:IN
$out = $env:OUT
$rows = [System.Collections.Generic.List[object]]::new()

function Add-UnixVolumes($Path, $Platform, $MountIndex) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "missing input: $Path" }
    $lines = Get-Content -LiteralPath $Path
    foreach ($line in $lines | Select-Object -Skip 1) {
        $fields = @($line -split '\s+')
        if ($fields.Count -le $MountIndex) { continue }
        $blocks = [double]$fields[1]
        $available = [double]$fields[3]
        if ($blocks -le 0) { throw "zero-sized $Platform volume: $line" }
        $mount = ($fields[$MountIndex..($fields.Count - 1)] -join ' ')
        $rows.Add([pscustomobject][ordered]@{
            platform=$Platform; volume=$mount; total_bytes=[long]($blocks * 1024)
            free_bytes=[long]($available * 1024); free_pct=[math]::Round($available * 100 / $blocks, 1)
        })
    }
}

Add-UnixVolumes (Join-Path $root 'linux/df.txt') 'linux' 5
Add-UnixVolumes (Join-Path $root 'macos/df.txt') 'macos' 8
$windowsPath = Join-Path $root 'windows/volumes.csv'
if (-not (Test-Path -LiteralPath $windowsPath -PathType Leaf)) { throw "missing input: $windowsPath" }
foreach ($volume in Import-Csv -LiteralPath $windowsPath) {
    $total = [long]$volume.Size
    $free = [long]$volume.SizeRemaining
    if ($total -le 0) { throw "zero-sized Windows volume: $($volume.DriveLetter)" }
    $rows.Add([pscustomobject][ordered]@{
        platform='windows'; volume=('{0}:\ ({1})' -f $volume.DriveLetter, $volume.FileSystemLabel)
        total_bytes=$total; free_bytes=$free; free_pct=[math]::Round($free * 100 / $total, 1)
    })
}

$low = @($rows | Where-Object { $_.free_pct -le 10 } | Sort-Object free_pct, platform, volume)
$low | Export-Csv -LiteralPath (Join-Path $out 'low_space.csv') -NoTypeInformation -Encoding utf8
$summary = [ordered]@{ volumes_seen=$rows.Count; low_space=$low.Count }
$summary | ConvertTo-Json -Compress | Set-Content -LiteralPath (Join-Path $out 'summary.json') -Encoding utf8

$ErrorActionPreference = 'Stop'
$root = $env:IN
$out = $env:OUT
$work = $env:WORK
$config = Get-Content -LiteralPath (Join-Path $root 'config.json') -Raw | ConvertFrom-Json
$python = Get-Command python3, python, py -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $python) { throw 'need Python 3' }
$workload = Join-Path $root 'workload.py'
$samples = [System.Collections.Generic.List[object]]::new()
$summaries = [System.Collections.Generic.List[object]]::new()
function Format-Seconds($Value) {
    return [string]::Format([Globalization.CultureInfo]::InvariantCulture, '{0:F6}', [double]$Value)
}

function Invoke-Benchmark($CaseName, $Iterations) {
    $arguments = @($workload, $CaseName, [string]$Iterations)
    if ($python.Name -eq 'py') { $arguments = @('-3') + $arguments }
    $clock = [System.Diagnostics.Stopwatch]::StartNew()
    $output = & $python.Source @arguments
    $exitCode = $LASTEXITCODE
    $clock.Stop()
    if ($exitCode -ne 0) { throw "benchmark failed: $CaseName (exit $exitCode)" }
    $checksum = ($output -join '').Trim()
    if ($checksum -notmatch '^\d+$') { throw "invalid checksum for $CaseName" }
    return [pscustomobject]@{ seconds=$clock.Elapsed.TotalSeconds; checksum=$checksum }
}

foreach ($case in $config.cases) {
    for ($i = 0; $i -lt $config.warmups; $i++) {
        [void](Invoke-Benchmark $case $config.iterations)
    }
    $times = [System.Collections.Generic.List[double]]::new()
    $checksum = $null
    for ($run = 1; $run -le $config.samples; $run++) {
        $result = Invoke-Benchmark $case $config.iterations
        if ($null -ne $checksum -and $checksum -ne $result.checksum) { throw "checksum changed for $case" }
        $checksum = $result.checksum
        $times.Add([double]$result.seconds)
        $samples.Add([pscustomobject][ordered]@{ case=$case; run=$run; seconds=(Format-Seconds $result.seconds); checksum=$checksum })
    }
    $ordered = @($times | Sort-Object)
    $middle = [int][math]::Floor($ordered.Count / 2)
    if ($ordered.Count % 2) { $median = $ordered[$middle] }
    else { $median = ($ordered[$middle - 1] + $ordered[$middle]) / 2 }
    $p95Index = [int][math]::Ceiling(0.95 * $ordered.Count) - 1
    $summaries.Add([pscustomobject][ordered]@{
        case=$case; samples=$ordered.Count; median_seconds=(Format-Seconds $median)
        p95_seconds=(Format-Seconds $ordered[$p95Index]); checksum=$checksum
    })
}
$samples | Sort-Object case, run | Export-Csv -LiteralPath (Join-Path $out 'samples.csv') -NoTypeInformation -Encoding utf8
$summaries | Sort-Object case | Export-Csv -LiteralPath (Join-Path $out 'summary.csv') -NoTypeInformation -Encoding utf8
[ordered]@{ cases=$config.cases.Count; warmups_per_case=$config.warmups; samples_per_case=$config.samples } |
    ConvertTo-Json -Compress | Set-Content -LiteralPath (Join-Path $out 'summary.json') -Encoding utf8

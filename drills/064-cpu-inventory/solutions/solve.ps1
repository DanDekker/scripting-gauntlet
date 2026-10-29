$ErrorActionPreference = 'Stop'
$root = $env:IN
$out = $env:OUT

function Read-Fields($Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "missing input: $Path" }
    $result = @{}
    foreach ($line in Get-Content -LiteralPath $Path) {
        if ($line -match '^\s*([^:]+):\s*(.*)$') { $result[$Matches[1].Trim()] = $Matches[2].Trim() }
    }
    return $result
}
function Normalize-Arch($Value) {
    if ($Value -match 'arm64|aarch64') { return 'arm64' }
    if ($Value -match 'x64|amd64|x86_64') { return 'x86_64' }
    throw "unknown architecture: $Value"
}

$linux = Read-Fields (Join-Path $root 'linux/lscpu.txt')
$mac = Read-Fields (Join-Path $root 'macos/sysctl.txt')
$macArch = Get-Content -LiteralPath (Join-Path $root 'macos/uname.txt') -Raw
$windows = Get-Content -LiteralPath (Join-Path $root 'windows/system.json') -Raw | ConvertFrom-Json
$linuxCores = [int]$linux['Core(s) per socket'] * [int]$linux['Socket(s)']
$linuxThreads = [int]$linux['CPU(s)']
$macCores = [int]$mac['hw.physicalcpu']
$macThreads = [int]$mac['hw.logicalcpu']
$winCores = [int](($windows.processors | Measure-Object -Property NumberOfCores -Sum).Sum)
$winThreads = [int](($windows.processors | Measure-Object -Property NumberOfLogicalProcessors -Sum).Sum)
$rows = @(
    [pscustomobject][ordered]@{ platform='linux'; processor=$linux['Model name']; physical_cores=$linuxCores; logical_cpus=$linuxThreads; threads_per_core=[int]($linuxThreads / $linuxCores); architecture=(Normalize-Arch $linux['Architecture']) }
    [pscustomobject][ordered]@{ platform='macos'; processor=$mac['machdep.cpu.brand_string']; physical_cores=$macCores; logical_cpus=$macThreads; threads_per_core=[int]($macThreads / $macCores); architecture=(Normalize-Arch $macArch) }
    [pscustomobject][ordered]@{ platform='windows'; processor=$windows.processors[0].Name; physical_cores=$winCores; logical_cpus=$winThreads; threads_per_core=[int]($winThreads / $winCores); architecture=(Normalize-Arch $windows.CsSystemType) }
)
$rows | Sort-Object platform | Export-Csv -LiteralPath (Join-Path $out 'cpus.csv') -NoTypeInformation -Encoding utf8
$summary = [ordered]@{ hosts=3; physical_cores=($linuxCores + $macCores + $winCores); logical_cpus=($linuxThreads + $macThreads + $winThreads) }
$summary | ConvertTo-Json -Compress | Set-Content -LiteralPath (Join-Path $out 'summary.json') -Encoding utf8

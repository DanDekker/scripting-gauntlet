$ErrorActionPreference = 'Stop'
$root = $env:IN
$out = $env:OUT

function Read-Required($Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "missing input: $Path" }
    return Get-Content -LiteralPath $Path -Raw
}
function Read-LinuxValue($Path, $Key) {
    foreach ($line in Get-Content -LiteralPath $Path) {
        if ($line -match ('^' + [regex]::Escape($Key) + '=(.*)$')) { return $Matches[1].Trim('"') }
    }
    throw "missing $Key in $Path"
}
function Read-MacValue($Path, $Key) {
    foreach ($line in Get-Content -LiteralPath $Path) {
        if ($line -match ('^' + [regex]::Escape($Key) + ':\s*(.*)$')) { return $Matches[1].Trim() }
    }
    throw "missing $Key in $Path"
}
function Normalize-Arch($Value) {
    if ($Value -match 'arm64|aarch64') { return 'arm64' }
    if ($Value -match 'x64|amd64|x86_64') { return 'x86_64' }
    throw "unknown architecture: $Value"
}

$linux = Join-Path $root 'linux'
$macos = Join-Path $root 'macos'
$windows = (Read-Required (Join-Path $root 'windows/computer.json')) | ConvertFrom-Json
$rows = @(
    [pscustomobject][ordered]@{
        platform = 'linux'; hostname = (Read-Required (Join-Path $linux 'hostname.txt')).Trim()
        name = Read-LinuxValue (Join-Path $linux 'os-release') 'NAME'
        version = Read-LinuxValue (Join-Path $linux 'os-release') 'VERSION_ID'
        architecture = Normalize-Arch (Read-Required (Join-Path $linux 'uname.txt')).Trim()
    }
    [pscustomobject][ordered]@{
        platform = 'macos'; hostname = (Read-Required (Join-Path $macos 'hostname.txt')).Trim()
        name = Read-MacValue (Join-Path $macos 'sw_vers.txt') 'ProductName'
        version = Read-MacValue (Join-Path $macos 'sw_vers.txt') 'ProductVersion'
        architecture = Normalize-Arch (Read-Required (Join-Path $macos 'uname.txt')).Trim()
    }
    [pscustomobject][ordered]@{
        platform = 'windows'; hostname = $windows.CsName; name = $windows.WindowsProductName
        version = $windows.WindowsVersion; architecture = Normalize-Arch $windows.CsSystemType
    }
)
$header = 'platform,hostname,name,version,architecture'
$csv = @($header) + @($rows | Sort-Object platform | ForEach-Object {
    '"{0}","{1}","{2}","{3}","{4}"' -f $_.platform, $_.hostname, $_.name, $_.version, $_.architecture
})
Set-Content -LiteralPath (Join-Path $out 'hosts.csv') -Value $csv -Encoding utf8
Set-Content -LiteralPath (Join-Path $out 'summary.json') -Value '{"platforms":3}' -Encoding utf8

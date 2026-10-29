$ErrorActionPreference = 'Stop'
$root = $env:IN
$work = $env:WORK
$out = $env:OUT
$ready = Join-Path $work 'ready.json'
$stop = Join-Path $work 'stop.flag'
$heartbeat = Join-Path $work 'heartbeat.txt'
$python = Get-Command python3, python, py -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $python) { throw 'need Python 3' }
$worker = Join-Path $root 'worker.py'
$start = [System.Diagnostics.ProcessStartInfo]::new()
$start.FileName = $python.Source
$start.UseShellExecute = $false
$start.RedirectStandardOutput = $true
$start.RedirectStandardError = $true
if ($python.Name -eq 'py') { $start.ArgumentList.Add('-3') }
$start.ArgumentList.Add($worker)
$start.ArgumentList.Add($ready)
$start.ArgumentList.Add($stop)
$start.ArgumentList.Add($heartbeat)
$child = [System.Diagnostics.Process]::Start($start)
$attached = $false
$stopped = $false
try {
    $deadline = [DateTime]::UtcNow.AddSeconds(5)
    while (-not (Test-Path -LiteralPath $ready) -and [DateTime]::UtcNow -lt $deadline) {
        $child.Refresh()
        if ($child.HasExited) { throw 'worker exited before ready' }
        Start-Sleep -Milliseconds 50
    }
    if (-not (Test-Path -LiteralPath $ready)) { throw 'worker readiness timed out' }
    $metadata = Get-Content -LiteralPath $ready -Raw | ConvertFrom-Json
    $readyPid = [int]$metadata.pid
    $port = [int]$metadata.port
    if ($readyPid -ne $child.Id) { throw 'worker PID mismatch' }
    $attachedProcess = Get-Process -Id $readyPid -ErrorAction Stop
    $attached = ($attachedProcess.Id -eq $child.Id)
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:$port/health" -TimeoutSec 2
    $listenerOk = ([string]$response).Trim() -eq 'ready'
    if (-not $listenerOk) { throw "listener probe failed on port $port" }
    $before = [int](Get-Content -LiteralPath $heartbeat -Raw)
    Start-Sleep -Milliseconds 120
    $after = [int](Get-Content -LiteralPath $heartbeat -Raw)
    if ($after -le $before) { throw 'heartbeat did not advance' }
} finally {
    Set-Content -LiteralPath $stop -Value 'stop' -Encoding utf8
    if (-not $child.WaitForExit(2000)) { $child.Kill(); $child.WaitForExit() }
    $child.Refresh()
    $stopped = $child.HasExited
}
if (-not $stopped) { throw 'worker still running' }
$report = [ordered]@{
    pid=[int]$child.Id; ready_pid=[int]$readyPid; port=[int]$port
    heartbeat_before=[int]$before; heartbeat_after=[int]$after
    attached=[bool]$attached; listener_ok=[bool]$listenerOk; stopped=[bool]$stopped
}
$report | ConvertTo-Json -Compress | Set-Content -LiteralPath (Join-Path $out 'attachment.json') -Encoding utf8

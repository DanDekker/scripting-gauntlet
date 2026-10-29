$ErrorActionPreference = 'Stop'
$root = $env:IN
$out = $env:OUT
$python = Get-Command python3, python, py -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $python) { throw 'need Python 3' }
$testFile = Join-Path $root 'test_case.py'
$rows = [System.Collections.Generic.List[object]]::new()
$ranDir = Join-Path $env:WORK 'ran'
New-Item -ItemType Directory -Path $ranDir -Force | Out-Null
$passed = 0
$failed = 0
foreach ($line in Get-Content -LiteralPath (Join-Path $root 'tests.txt')) {
    $name = $line.Trim()
    if (-not $name -or $name.StartsWith('#')) { continue }
    if ($name -notmatch '^[a-z-]+$') { throw "bad test name: $name" }
    $arguments = @($testFile, $name)
    if ($python.Name -eq 'py') { $arguments = @('-3') + $arguments }
    $stdout = @(& $python.Source @arguments 2> (Join-Path $env:WORK 'stderr.txt')) -join ' '
    $code = $LASTEXITCODE
    $stderrContent = Get-Content -LiteralPath (Join-Path $env:WORK 'stderr.txt') -Raw -ErrorAction SilentlyContinue
    if ($null -eq $stderrContent) { $stderr = '' } else { $stderr = $stderrContent.Trim() }
    if ($code -eq 0) { $passed++ } else { $failed++ }
    $rows.Add([pscustomobject][ordered]@{
        test=$name; exit_code=$code; stdout=$stdout.Replace(',', ';'); stderr=$stderr.Replace(',', ';')
    })
    Set-Content -LiteralPath (Join-Path $ranDir $name) -Value $code -Encoding utf8
}
$rows | Export-Csv -LiteralPath (Join-Path $out 'results.csv') -NoTypeInformation -Encoding utf8
[ordered]@{ tests=$rows.Count; passed=$passed; failed=$failed } |
    ConvertTo-Json -Compress | Set-Content -LiteralPath (Join-Path $out 'summary.json') -Encoding utf8
if ($failed -gt 0) { throw "$failed test(s) failed" }

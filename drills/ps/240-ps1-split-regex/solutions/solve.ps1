# 240-ps1-split-regex — escape the regex metacharacters; the pipe is alternation.
$ErrorActionPreference = 'Stop'
$in = $env:IN; $out = $env:OUT
if (-not $in) { throw 'IN not set' }
if (-not $out) { throw 'OUT not set' }

$rows = [System.Collections.Generic.List[object]]::new()
$packages = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
$malformed = 0
$total = 0

foreach ($line in Get-Content (Join-Path $in 'builds.log')) {
    $text = ([string]$line).Trim()
    if (-not $text -or $text.StartsWith('#')) { continue }

    # '|' is alternation and '.' is any-char: both need escaping to act as delimiters.
    $fields = $text -split '\|'
    if ($fields.Count -ne 4) { $malformed++; continue }

    $pkg = $fields[0].Trim()
    $ver = $fields[1].Trim()
    $sha = $fields[2].Trim()
    $sizeText = $fields[3].Trim()

    if (-not $pkg -or $ver -notmatch '^\d+\.\d+\.\d+$' -or $sizeText -notmatch '^\d+$') {
        $malformed++
        continue
    }

    $v = $ver -split '\.'
    $size = [long]$sizeText
    $total += $size
    $null = $packages.Add($pkg)

    $rows.Add([pscustomobject]@{
        pkg   = $pkg
        major = [int]$v[0]
        minor = [int]$v[1]
        patch = [int]$v[2]
        sha   = $sha
        size  = $size
    })
}

if ($rows.Count -gt 0) {
    $rows | Export-Csv -Path (Join-Path $out 'builds.csv') -NoTypeInformation -Encoding utf8
}
else {
    Set-Content -Path (Join-Path $out 'builds.csv') -Value 'pkg,major,minor,patch,sha,size' -Encoding utf8
}

@{
    rows       = $rows.Count
    malformed  = $malformed
    total_size = $total
    packages   = $packages.Count
} | ConvertTo-Json -Compress | Set-Content -Path (Join-Path $out 'summary.json') -Encoding utf8

#!/usr/bin/env pwsh
# 003-http-probe — Invoke-RestMethod, object pipeline, no parsing.
$ErrorActionPreference = 'Stop'

if (-not $env:API_BASE) { throw 'API_BASE not set' }
$base = $env:API_BASE
$out = $env:OUT
New-Item -ItemType Directory -Force -Path $out | Out-Null

$health = Invoke-RestMethod -Uri "$base/health" -Method Get
if (-not $health.ok) {
    throw "service reports unhealthy: $($health | ConvertTo-Json -Compress)"
}

$items = @()
$pages = 0
$next = '/api/v1/items?page=1'
$visited = [System.Collections.Generic.HashSet[string]]::new()

while ($next) {
    if (-not $visited.Add($next)) { throw "pagination loop at $next" }
    $pages++
    if ($pages -gt 50) { throw 'exceeded 50 pages' }

    $page = Invoke-RestMethod -Uri "$base$next" -Method Get
    $items += $page.items
    $next = $page.next
}

$sorted = @($items | Sort-Object -Property id)
$sorted | ConvertTo-Json -Depth 5 | Set-Content -Path (Join-Path $out 'items.json') -Encoding utf8NoBOM

$report = [ordered]@{
    ok         = $true
    version    = $health.version
    item_count = $sorted.Count
    pages      = $pages
}
$report | ConvertTo-Json -Depth 5 | Set-Content -Path (Join-Path $out 'report.json') -Encoding utf8NoBOM

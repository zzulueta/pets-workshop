<#
Simple PowerShell script to create GitHub issues from markdown files in .github/ISSUES.
Usage:
  $env:GITHUB_TOKEN = 'ghp_...'
  pwsh ./scripts/create_github_issues.ps1

Requires an environment variable GITHUB_TOKEN with repo:issues permissions.
#>

$owner = 'zzulueta'
$repo = 'pets-workshop'
$issuesDir = Join-Path -Path $PSScriptRoot -ChildPath '..\.github\ISSUES' | Resolve-Path -Relative
$token = $env:GITHUB_TOKEN
if (-not $token) {
    Write-Error "GITHUB_TOKEN environment variable not set. Export it and rerun the script."
    exit 1
}

Get-ChildItem -Path (Join-Path $PSScriptRoot '..\.github\ISSUES') -Filter '*.md' | ForEach-Object {
    $path = $_.FullName
    $lines = Get-Content -Path $path -Raw -ErrorAction Stop
    # Use first non-empty line as title, rest as body
    $all = $lines -split "\r?\n"
    $titleLine = ($all | Where-Object { $_.Trim() -ne '' } | Select-Object -First 1)
    $body = ($all | SkipWhile { $_ -ne $titleLine } | Select-Object -Skip 1) -join "`n"

    $payload = @{ title = $titleLine; body = $body } | ConvertTo-Json -Depth 5
    $uri = "https://api.github.com/repos/$owner/$repo/issues"

    Write-Host "Creating issue:`n Title: $titleLine`n From file: $path"
    try {
        $resp = Invoke-RestMethod -Uri $uri -Method Post -Headers @{ Authorization = "Bearer $token"; Accept = 'application/vnd.github+json'; 'User-Agent' = 'create-github-issues-script' } -Body $payload -ContentType 'application/json'
        Write-Host "Created: $($resp.html_url)"
    } catch {
        Write-Error "Failed to create issue from $path: $_"
    }
}

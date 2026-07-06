# Install git hooks for secret scanning (pre-commit + pre-push).
# Run from the repository root: .\scripts\install-git-hooks.ps1

$ErrorActionPreference = "Stop"
$Root = (git rev-parse --show-toplevel 2>$null)
if (-not $Root) {
    Write-Error "Not inside a git repository."
}
Set-Location $Root

$HooksDir = Join-Path $Root ".git\hooks"
$GithooksDir = Join-Path $Root ".githooks"

function Install-FallbackHooks {
    foreach ($name in @("pre-commit", "pre-push")) {
        $src = Join-Path $GithooksDir $name
        $dest = Join-Path $HooksDir $name
        if (-not (Test-Path $src)) {
            Write-Error "Missing $src"
        }
        Copy-Item -Path $src -Destination $dest -Force
        Write-Host "Installed fallback hook: $dest"
    }
}

function Find-PreCommit {
    if (Get-Command pre-commit -ErrorAction SilentlyContinue) {
        return "pre-commit"
    }
    $venvScripts = Join-Path $Root "prosocial_platform\.venv\Scripts\pre-commit.exe"
    if (Test-Path $venvScripts) {
        return $venvScripts
    }
    $venvBin = Join-Path $Root "prosocial_platform\.venv\bin\pre-commit"
    if (Test-Path $venvBin) {
        return $venvBin
    }
    return $null
}

$preCommit = Find-PreCommit
if ($preCommit) {
    Write-Host "Installing hooks via pre-commit ($preCommit)..."
    & $preCommit install --hook-type pre-commit --hook-type pre-push
    Write-Host "pre-commit hooks installed (includes gitleaks + secret guard)."
} else {
    Write-Warning "pre-commit not found; installing fallback shell hooks from .githooks/"
    Write-Warning "For gitleaks scanning, install pre-commit: pip install pre-commit"
    Write-Warning "Or install gitleaks: https://github.com/gitleaks/gitleaks#installing"
    Install-FallbackHooks
}

Write-Host ""
Write-Host "Secret guards active before commit and push:"
Write-Host "  - Blocks .env / .env.local / *.pem / *.key and tracked bytecode"
Write-Host "  - Scans with gitleaks (high-entropy secrets and provider patterns)"
Write-Host "  - Flags dev settings or seed_test_data in deployment configs"
Write-Host ""
Write-Host "Emergency bypass (rotate credentials afterward): GITLEAKS_DISABLE=1 git push"

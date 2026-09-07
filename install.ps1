$ErrorActionPreference = "Stop"
$Repo = "JDsnyke/hermes-privacy-stack"
$Root = if ($env:HERMES_PRIVACY_STACK_HOME) { $env:HERMES_PRIVACY_STACK_HOME } else { Join-Path $HOME ".hermes-privacy-stack" }

$Here = if ($PSScriptRoot) { $PSScriptRoot } else { $null }
if ($Here -and (Test-Path (Join-Path $Here "bootstrap.py"))) {
    $Root = $Here
} elseif (-not (Test-Path (Join-Path $Root "bootstrap.py"))) {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "Git is required." }
    git clone --depth 1 "https://github.com/$Repo.git" $Root
}

$Python = Get-Command python -ErrorAction SilentlyContinue
if (-not $Python) { $Python = Get-Command py -ErrorAction SilentlyContinue }
if (-not $Python) { throw "Python 3.10+ is required." }

$SkipGuided = ($env:HPS_SKIP_GUIDED -eq "1") -or ($args -contains "--non-interactive") -or ($args -contains "--self-test")

if ($Python.Name -eq "py.exe") {
    & py -3 (Join-Path $Root "bootstrap.py") @args
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    if (-not $SkipGuided -and (Test-Path (Join-Path $Root "scripts\guided_setup.py"))) {
        & py -3 (Join-Path $Root "scripts\guided_setup.py")
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
} else {
    & $Python.Source (Join-Path $Root "bootstrap.py") @args
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    if (-not $SkipGuided -and (Test-Path (Join-Path $Root "scripts\guided_setup.py"))) {
        & $Python.Source (Join-Path $Root "scripts\guided_setup.py")
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
}

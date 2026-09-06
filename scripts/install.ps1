$ErrorActionPreference = 'Stop'
$ProfileRepo = Split-Path -Parent $PSScriptRoot
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw 'Install uv first: https://docs.astral.sh/uv/getting-started/installation/'
}
& uv run --project $ProfileRepo --locked python (Join-Path $PSScriptRoot 'profile/manage.py') @args
exit $LASTEXITCODE

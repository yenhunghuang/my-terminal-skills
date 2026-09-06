$ErrorActionPreference = 'Stop'
$ProfileRepo = Split-Path -Parent $PSScriptRoot
& git -C $ProfileRepo pull --ff-only
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& (Join-Path $PSScriptRoot 'install.ps1') install @args
exit $LASTEXITCODE

$ErrorActionPreference = 'Stop'
$global:status = 0

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Label,

        [Parameter(Mandatory = $true)]
        [scriptblock]$Action
    )

    Write-Host ""
    Write-Host "==================================================" 
    Write-Host "==> $Label"
    Write-Host "=================================================="

    try {
        & $Action
        if ($LASTEXITCODE -eq 0) {
            Write-Host "PASS: $Label"
            Write-Host ""
            return
        }

        Write-Host "FAIL: $Label (exit $LASTEXITCODE)"
        Write-Host ""
        $global:status = 1
    }
    catch {
        Write-Host "FAIL: $Label"
        Write-Host $_.Exception.Message
        Write-Host ""
        $global:status = 1
    }
}

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python is required but not installed or not on PATH."
    exit 127
}

Invoke-Step "Python Kernel Testbench" {
    python .\tests\testbench.py
}

if (Get-Command make -ErrorAction SilentlyContinue) {
    Invoke-Step "C SDK tests" {
        cmd /c "cd /d `"$repoRoot\sdk`" && make clean && make test"
    }
}
else {
    Write-Host ""
    Write-Host "=================================================="
    Write-Host "==> C SDK tests skipped"
    Write-Host "=================================================="
    Write-Host "make is not installed in this environment."
    Write-Host "Install MSYS2/MinGW or Git for Windows with make, then rerun."
    Write-Host ""
}

if (Test-Path ".\kicad\scripts\gen_bga144_footprint.py") {
    Invoke-Step "KiCad BGA footprint generation" {
        python .\kicad\scripts\gen_bga144_footprint.py
    }
}
else {
    Write-Host ""
    Write-Host "=================================================="
    Write-Host "==> KiCad footprint generator not found"
    Write-Host "=================================================="
    Write-Host "The file kicad/scripts/gen_bga144_footprint.py is missing."
    Write-Host ""
    $global:status = 1
}

if (Test-Path ".\fpga\litex\target_oq_dhc.py") {
    $litexAvailable = $false
    try {
        python -c "import litex" 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $litexAvailable = $true
        }
    }
    catch {
        $litexAvailable = $false
    }

    if ($litexAvailable) {
        Invoke-Step "LiteX FPGA target build" {
            cmd /c "cd /d `"$repoRoot\fpga\litex`" && python target_oq_dhc.py --build"
        }
    }
    else {
        Write-Host ""
        Write-Host "=================================================="
        Write-Host "==> LiteX FPGA build skipped"
        Write-Host "=================================================="
        Write-Host "LiteX is not installed in the current environment."
        Write-Host "Install LiteX and rerun: cd fpga\litex; python target_oq_dhc.py --build"
        Write-Host ""
    }
}
else {
    Write-Host ""
    Write-Host "=================================================="
    Write-Host "==> LiteX target not found"
    Write-Host "=================================================="
    Write-Host "fpga/litex/target_oq_dhc.py does not exist in this checkout."
    Write-Host ""
}

Write-Host ""
if ($global:status -eq 0) {
    Write-Host "ALL CHECKS COMPLETED WITHOUT FAILURES"
}
else {
    Write-Host "ONE OR MORE CHECKS FAILED"
}

exit $global:status

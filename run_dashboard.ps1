# Pocket Option Data Harvester - Instant Dashboard Launcher
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path $scriptDir

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "   POCKET OPTION 24/7 MARKET DATA HARVESTER (AI/ML ENGINE)" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Locate Python
$pythonBin = "python"
$venvPath1 = Join-Path $scriptDir ".venv\Scripts\python.exe"
$venvPath2 = Join-Path $scriptDir "venv\Scripts\python.exe"

if (Test-Path $venvPath1) {
    $pythonBin = $venvPath1
    Write-Host "[OK] Using local virtual environment (.venv)" -ForegroundColor DarkGray
} elseif (Test-Path $venvPath2) {
    $pythonBin = $venvPath2
    Write-Host "[OK] Using local virtual environment (venv)" -ForegroundColor DarkGray
} else {
    $systemPython = Get-Command python -ErrorAction SilentlyContinue
    if ($systemPython) {
        $pythonBin = $systemPython.Source
        Write-Host "[OK] Using system Python: $pythonBin" -ForegroundColor DarkGray
    } else {
        $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
        if ($pyLauncher) {
            $pythonBin = "py"
            Write-Host "[OK] Using Python launcher (py)" -ForegroundColor DarkGray
        } else {
            Write-Host "[ERROR] Python was not found on your system." -ForegroundColor Red
            Write-Host "Please install Python 3.10+ from https://www.python.org/downloads/ and check 'Add to PATH'." -ForegroundColor Yellow
            pause
            exit 1
        }
    }
}

# 2. Check dependencies
Write-Host "[*] Checking runtime dependencies..." -ForegroundColor Cyan
& $pythonBin -c "import fastapi, uvicorn, websockets, aiosqlite, pydantic" *>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Missing packages detected. Installing requirements.txt..." -ForegroundColor Yellow
    & $pythonBin -m pip install -r (Join-Path $scriptDir "requirements.txt")
} else {
    Write-Host "[OK] All dependencies verified." -ForegroundColor Green
}

# 3. Determine URL
$port = 8000
if ($env:PORT) {
    $port = [int]$env:PORT
}
$targetUrl = "http://localhost:$port"

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  Dashboard URL: $targetUrl" -ForegroundColor Green
Write-Host "  Health Status: $targetUrl/healthz" -ForegroundColor DarkGray
Write-Host "  Collector API: $targetUrl/api/status" -ForegroundColor DarkGray
Write-Host "  Press Ctrl + C in this window to stop the server anytime." -ForegroundColor Yellow
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

# 4. Auto-launch default browser in background after 2 seconds
Start-Job -ScriptBlock {
    param($url)
    Start-Sleep -Seconds 2
    Start-Process $url
} -ArgumentList $targetUrl | Out-Null

# 5. Start Dashboard
& $pythonBin (Join-Path $scriptDir "run_dashboard.py")

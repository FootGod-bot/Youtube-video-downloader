# --- Check if Python is installed ---
Write-Host "Checking for Python..."
$pythonInstalled = $false
try {
    $pyVersion = py --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        $pythonInstalled = $true
        Write-Host "Python already installed: $pyVersion"
    }
} catch {}

# --- Check if Python Install Manager is installed ---
Write-Host "Checking for Python Install Manager..."
$managerInstalled = $false
try {
    $managerVersion = py --list-paths 2>$null
    if ($LASTEXITCODE -eq 0) {
        $managerInstalled = $true
        Write-Host "Python Install Manager already installed."
    }
} catch {}

# --- Install Python Install Manager if missing ---
if (-not $managerInstalled) {
    Write-Host "Installing Python Install Manager..."
    winget install Python.PythonInstallManager -h --accept-package-agreements --accept-source-agreements
}

# --- Install Python 3.13 if missing ---
if (-not $pythonInstalled) {
    Write-Host "Installing Python 3.13..."
    py install 3.13 --global
} else {
    Write-Host "Python already installed — skipping."
}

Write-Host "Done."

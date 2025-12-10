# Youtube Downloader Full Installer
$ErrorActionPreference = "Stop"

$InstallDir = "C:\Program Files\Youtube_download"
$RepoUrl = "https://github.com/FootGod-bot/Youtube-video-downloader.git"
$TempDir = Join-Path $env:TEMP "ytdl_installer_$([guid]::NewGuid().ToString('N'))"
$StartupDir = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"

# Ensure running as admin
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Relaunching as Administrator..."
    Start-Process powershell "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    Exit
}

# Create directories
New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
New-Item -ItemType Directory -Path $TempDir -Force | Out-Null

# Clone repo (or download zip if git missing)
if (Get-Command git -ErrorAction SilentlyContinue) {
    git clone --depth 1 $RepoUrl $TempDir
} else {
    $zipUrl = $RepoUrl -replace '\.git$','' + "/archive/refs/heads/main.zip"
    $zipPath = Join-Path $TempDir "repo.zip"
    Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath -UseBasicParsing
    Expand-Archive -LiteralPath $zipPath -DestinationPath $TempDir
    $inner = Get-ChildItem -Path $TempDir | Where-Object {$_.PSIsContainer} | Select-Object -First 1
    if ($inner) {
        Get-ChildItem $inner.FullName | ForEach-Object { Move-Item $_.FullName -Destination $TempDir -Force }
        Remove-Item $inner.FullName -Recurse -Force
    }
}

# Copy files to install folder
Copy-Item -Path (Join-Path $TempDir '*') -Destination $InstallDir -Recurse -Force

# Create empty queue folder
New-Item -ItemType Directory -Path (Join-Path $InstallDir "queue") -Force | Out-Null

# Install yt-dlp via winget
Write-Host "Installing yt-dlp..."
winget install --id=yt-dlp.yt-dlp -e --accept-package-agreements --accept-source-agreements --silent

# Install FFmpeg via winget
Write-Host "Installing FFmpeg..."
winget install ffmpeg --accept-package-agreements --accept-source-agreements --silent

# Force install Deno
Write-Host "Installing Deno..."
try { iex (iwr "https://deno.land/install.ps1" -UseBasicParsing).Content } catch { Write-Warning "Deno installation failed: $_" }

# Check if Python Install Manager exists
$pyExists = $false
try {
    $output = py list 2>&1
    if ($output -match "Python install manager") { $pyExists = $true }
} catch {
    $pyExists = $false
}

# Install Python Install Manager via winget if missing
if (-not $pyExists) {
    Write-Host "Python Install Manager not found. Installing via winget..."
    winget install --id=Python.PythonInstallManager -e --silent
} else {
    Write-Host "Python Install Manager already installed."
}

# Update manager
Write-Host "Updating Python Install Manager..."
Start-Process -FilePath "py" -ArgumentList "update" -Wait -NoNewWindow

# Install Python 3.13.9 via manager
Write-Host "Installing Python 3.13.9..."
Start-Process -FilePath "py" -ArgumentList "install 3.13.9" -Wait -NoNewWindow

# Confirm Python installation
py list

# Add install folder to user PATH if not present
$UserPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($UserPath -notlike "*$InstallDir*") {
    [Environment]::SetEnvironmentVariable("PATH", "$UserPath;$InstallDir", "User")
    Write-Host "Added $InstallDir to user PATH."
} else {
    Write-Host "$InstallDir already in PATH."
}

# Create single .bat to run all three scripts
$BatContent = "@echo off`n" +
"python `"$InstallDir\downloader.py`"`n" +
"python `"$InstallDir\formatter.py`"`n" +
"python `"$InstallDir\ytlinkserver.py`"`n" +
"pause"
$BatPath = Join-Path $InstallDir "run_all.bat"
Set-Content -Path $BatPath -Value $BatContent -Encoding ASCII

# Copy .bat to startup folder
$StartupBat = Join-Path $StartupDir "run_ytdl_startup.bat"
Copy-Item -Path $BatPath -Destination $StartupBat -Force

# Cleanup temp folder
Remove-Item -Path $TempDir -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "`nInstallation complete! Installed to $InstallDir"
Write-Host "Restart your terminal to apply PATH changes if you want to run scripts from anywhere."

# ------------------------------
# YouTube Downloader Installer
# ------------------------------

$installPath = "C:\Program Files\YouTube-Downloader"
$startupPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"

# --- create install folder ---
if (!(Test-Path $installPath)) {
    New-Item -ItemType Directory -Path $installPath | Out-Null
}

# --- create extension subfolder ---
$extPath = Join-Path $installPath "extension"
if (!(Test-Path $extPath)) {
    New-Item -ItemType Directory -Path $extPath | Out-Null
}

# --- copy backend files ---
$repoFiles = @(
    "ytlinkserver.py",
    "formatter.py",
    "downloader.py",
    "config.json"
)

foreach ($f in $repoFiles) {
    if (Test-Path $f) {
        Copy-Item $f $installPath -Force
    }
}

# --- copy extension files ---
$extFiles = @(
    "content.js",
    "manifest.json",
    "icon48.png",
    "icon128.png"
)

foreach ($f in $extFiles) {
    if (Test-Path $f) {
        Copy-Item $f $extPath -Force
    }
}

# --- install deps ---
Write-Host "Installing ffmpeg..."
winget install --id Gyan.FFmpeg --silent

Write-Host "Installing deno..."
winget install --id DenoLand.Deno --silent

Write-Host "Installing yt-dlp..."
winget install --id yt-dlp.yt-dlp --silent

# --- update PATH ---
$paths = @(
    $installPath,
    "C:\Program Files\FFmpeg\bin",
    "C:\Program Files\Deno\bin"
)

foreach ($p in $paths) {
    if (Test-Path $p) {
        # Append only if not already in PATH
        if ($env:PATH -notlike "*$p*") {
            setx PATH "$($env:PATH);$p" > $null
        }
    }
}

# --- create launcher script content ---
$launcher = @'
# Auto launcher for YouTube Downloader

Write-Host "Starting ytlinkserver..."
powershell -WindowStyle Hidden -Command "python \"C:\Program Files\YouTube-Downloader\ytlinkserver.py\""
Start-Sleep -Seconds 5

Write-Host "Starting formatter..."
powershell -WindowStyle Hidden -Command "python \"C:\Program Files\YouTube-Downloader\formatter.py\""
Start-Sleep -Seconds 5

Write-Host "Starting downloader..."
powershell -WindowStyle Hidden -Command "python \"C:\Program Files\YouTube-Downloader\downloader.py\""
'@

# --- write launcher in install folder ---
$launcherFile = Join-Path $installPath "launcher.ps1"
Set-Content -Path $launcherFile -Value $launcher -Force

# --- write launcher in startup folder ---
$startupLauncher = Join-Path $startupPath "YouTube-Downloader-Launcher.ps1"
Set-Content -Path $startupLauncher -Value $launcher -Force

Write-Host "Install complete."

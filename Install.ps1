# ------------------------------
# YouTube Downloader Installer
# ------------------------------

# --- admin check ---
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltinRole] "Administrator")) {
    Write-Warning "You must run this installer as Administrator. Restarting with admin privileges..."
    Start-Process powershell "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$installPath = "C:\Program Files\YouTube-Downloader"
$extPath = Join-Path $installPath "extension"
$startupPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$wingetLinks = "$env:LocalAppData\Microsoft\WinGet\Links"

# --- create folders ---
foreach ($p in @($installPath, $extPath)) {
    if (!(Test-Path $p)) { New-Item -ItemType Directory -Path $p | Out-Null }
}

# --- function to download GitHub files ---
function Download-GitHubFile {
    param(
        [string]$url,
        [string]$dest
    )
    $wc = New-Object System.Net.WebClient
    $wc.Headers.Add("user-agent","PowerShell")
    Write-Host "Downloading $dest..."
    $wc.DownloadFile($url, $dest)
    $wc.Dispose()
}

# --- GitHub raw file URLs ---
$repoFiles = @{
    "ytlinkserver.py" = "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/files/ytlinkserver.py"
    "formatter.py"    = "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/files/formatter.py"
    "downloader.py"   = "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/files/Downloader.py"
    "config.json"     = "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/files/config.json"
}

$extFiles = @{
    "content.js"      = "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/files/extention_files/content.js"
    "manifest.json"   = "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/files/extention_files/manifest.json"
    "icon48.png"      = "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/files/extention_files/icon48.png"
    "icon128.png"     = "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/files/extention_files/icon128.png"
}

# --- download backend files ---
foreach ($f in $repoFiles.Keys) {
    $dest = Join-Path $installPath $f
    Download-GitHubFile $repoFiles[$f] $dest
}

# --- download extension files ---
foreach ($f in $extFiles.Keys) {
    $dest = Join-Path $extPath $f
    Download-GitHubFile $extFiles[$f] $dest
}

# --- install deps via winget ---
Write-Host "Installing ffmpeg..."
winget install --id Gyan.FFmpeg --silent

Write-Host "Installing deno..."
winget install --id DenoLand.Deno --silent

Write-Host "Installing yt-dlp..."
winget install --id yt-dlp.yt-dlp --silent

# --- update SYSTEM PATH ---
$systemPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
foreach ($p in @($installPath, $wingetLinks)) {
    if ($systemPath -notlike "*$p*") {
        $systemPath += ";$p"
    }
}
[Environment]::SetEnvironmentVariable("Path", $systemPath, "Machine")

# --- create launcher content ---
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

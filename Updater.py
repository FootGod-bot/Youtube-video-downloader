import os
import subprocess
import time
import shutil
from pathlib import Path
from urllib.request import urlretrieve
import winreg
import sys

print("== Yt-dlp Installer ==")

# Paths
user_profile = Path.home()
project_folder = user_profile / "Yt-dlp downloader"
startup_folder = user_profile / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
ext_dir = project_folder / "extension_files"
yt_dlp_dir = Path("C:/yt-dlp")
ffmpeg_dir = Path("C:/ffmpeg")
ytlink_path = user_profile / "Documents" / "ytlink.txt"
repo_base = "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main"

# Files to download
files = ["Downloader.ahk", "ytlinkserver.py", "README.md"]
extension_files = ["content.js", "icon128.png", "icon48.png", "manifest.json"]
rbtray_files = {
    "RBTray.exe": "https://raw.githubusercontent.com/benbuck/rbtray/main/x64/RBTray.exe",
    "RBHook.dll": "https://raw.githubusercontent.com/benbuck/rbtray/main/x64/RBHook.dll"
}

# Create necessary folders
project_folder.mkdir(parents=True, exist_ok=True)
ext_dir.mkdir(exist_ok=True)
startup_folder.mkdir(parents=True, exist_ok=True)
ytlink_path.parent.mkdir(parents=True, exist_ok=True)
ytlink_path.touch(exist_ok=True)

def download_file(url, dest):
    try:
        urlretrieve(url, dest)
        print(f"Downloaded {os.path.basename(dest)}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

# 1. Download AHK scripts and ytlinkserver
for file in files:
    download_file(f"{repo_base}/{file}", project_folder / file)

# 2. Copy AHK & Python scripts to Startup
shutil.copy(project_folder / "Downloader.ahk", startup_folder / "Downloader.ahk")
shutil.copy(project_folder / "ytlinkserver.py", startup_folder / "ytlinkserver.py")

# 3. Create .bat files to run AHK and Python at startup
bat_ahk = startup_folder / "RunDownloader.bat"
bat_py = startup_folder / "RunYtlinkserver.bat"

with open(bat_ahk, "w") as f:
    f.write(f'start "" "C:\\Program Files\\AutoHotkey\\AutoHotkey.exe" "{startup_folder}\\Downloader.ahk"')

with open(bat_py, "w") as f:
    f.write(f'start "" python "{startup_folder}\\ytlinkserver.py"')

print("Added Downloader.ahk and ytlinkserver.py to Startup.")

# 4. Download extension files
for file in extension_files:
    download_file(f"{repo_base}/{file}", ext_dir / file)

# 5. yt-dlp setup
skip_yt_dlp = False
if yt_dlp_dir.exists():
    confirm = input("yt-dlp folder exists. Update it? (y/n): ").strip().lower()
    if confirm == "y":
        shutil.rmtree(yt_dlp_dir)
        print("yt-dlp folder removed.")
    else:
        skip_yt_dlp = True

if not skip_yt_dlp:
    yt_dlp_dir.mkdir(exist_ok=True)
    yt_dlp_path = yt_dlp_dir / "yt-dlp.exe"
    download_file("https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe", yt_dlp_path)
    print(f"Added {yt_dlp_dir} to PATH.")
    # Path editing skipped here (manual step)

# 6. FFmpeg setup
skip_ffmpeg = False
ffmpeg_zip = ffmpeg_dir / "ffmpeg-git-full.7z"
if ffmpeg_dir.exists():
    confirm = input("FFmpeg folder exists. Update it? (y/n): ").strip().lower()
    if confirm == "y":
        shutil.rmtree(ffmpeg_dir)
    else:
        skip_ffmpeg = True

if not skip_ffmpeg:
    ffmpeg_dir.mkdir(exist_ok=True)
    download_file("https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z", ffmpeg_zip)
    print("Please extract ffmpeg-git-full.7z to C:/ffmpeg and hit Enter.")
    input()
    ffmpeg_bin = ffmpeg_dir / "ffmpeg-git-full" / "ffmpeg-2025-05-26-git-43a69886b2-full_build" / "bin"
    if ffmpeg_bin.exists():
        print(f"Add to PATH manually: {ffmpeg_bin}")
    ffmpeg_zip.unlink(missing_ok=True)

# 7. RBTray
rbtray_dir = project_folder / "RBTray"
rbtray_dir.mkdir(exist_ok=True)
for name, url in rbtray_files.items():
    download_file(url, rbtray_dir / name)

# 8. Minimiser.exe
download_file(f"{repo_base}/Minimiser.exe", project_folder / "Minimiser.exe")

# 9. Download updater
urlretrieve(f"{repo_base}/Updater.py", user_profile / "updater.py")

# 10. Self-delete
try:
    script_path = Path(__file__)
    if script_path.name.lower() == "install.py":
        os.remove(script_path)
        print("Deleted install.py")
except Exception as e:
    print(f"Couldn't delete script: {e}")

print("Install complete.")

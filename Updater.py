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
ext_dir = project_folder / "extension_files"
yt_dlp_dir = Path("C:/yt-dlp")
ffmpeg_dir = Path("C:/ffmpeg")
ytlink_path = user_profile / "OneDrive" / "Documentos" / "ytlink.txt"
startup_dir = user_profile / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"

repo_base = "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main"

files = ["Downloader.ahk", "ytlinkserver.py", "README.md"]
extension_files = ["content.js", "icon128.png", "icon48.png", "manifest.json"]
ffmpeg_zip = ffmpeg_dir / "ffmpeg-git-full.7z"

# Helper functions
def download_file(url, dest):
    try:
        urlretrieve(url, dest)
        print(f"Downloaded {os.path.basename(dest)}")
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

def run_installer(installer_path):
    print("Running AutoHotkey installer...")
    subprocess.run([str(installer_path)], check=False)
    print("Installer finished.")
    for _ in range(5):
        try:
            installer_path.unlink()
            print("Deleted installer.")
            break
        except:
            time.sleep(1)

def add_to_user_path(new_path):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment', 0, winreg.KEY_READ) as key:
            existing_path, _ = winreg.QueryValueEx(key, "PATH")
    except FileNotFoundError:
        existing_path = ""
    if new_path.lower() not in existing_path.lower():
        updated_path = existing_path + ";" + new_path if existing_path else new_path
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment', 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, updated_path)
        print(f"Added {new_path} to PATH.")
    else:
        print(f"{new_path} already in PATH.")

def ahk_installed():
    for path in os.environ["PATH"].split(";"):
        if Path(path.strip('"')) / "AutoHotkey.exe" in Path(path).glob("AutoHotkey.exe"):
            return True
    return False

def create_shortcut(name, target, args="", working_dir=""):
    path = startup_dir / f"{name}.lnk"
    if path.exists():
        try:
            path.unlink()
        except:
            print(f"Could not delete existing shortcut: {path}")
    script = f'''
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{path}")
$Shortcut.TargetPath = "{target}"
$Shortcut.Arguments = "{args}"
$Shortcut.WorkingDirectory = "{working_dir or os.path.dirname(target)}"
$Shortcut.Save()
'''
    subprocess.run(["powershell", "-Command", script])

# Setup
project_folder.mkdir(parents=True, exist_ok=True)
ext_dir.mkdir(exist_ok=True)
ytlink_path.parent.mkdir(parents=True, exist_ok=True)
ytlink_path.touch(exist_ok=True)
startup_dir.mkdir(parents=True, exist_ok=True)

# 1. AutoHotkey
ahk_installer = project_folder / "AutoHotkey_Installer.exe"
if not ahk_installed():
    if download_file("https://www.autohotkey.com/download/ahk-v2.exe", ahk_installer):
        run_installer(ahk_installer)
    else:
        print("Failed to download AutoHotkey. Install manually.")
else:
    print("AutoHotkey already installed.")

# 2. Downloader files
for file in files:
    download_file(f"{repo_base}/{file}", project_folder / file)
for file in extension_files:
    download_file(f"{repo_base}/{file}", ext_dir / file)

# 3. yt-dlp
skip_yt_dlp = False
if yt_dlp_dir.exists():
    confirm = input("yt-dlp folder exists. Update it? (y/n): ").strip().lower()
    if confirm == "y":
        shutil.rmtree(yt_dlp_dir)
    else:
        skip_yt_dlp = True

if not skip_yt_dlp:
    yt_dlp_dir.mkdir(exist_ok=True)
    yt_dlp_path = yt_dlp_dir / "yt-dlp.exe"
    if download_file("https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe", yt_dlp_path):
        add_to_user_path(str(yt_dlp_dir))

# 4. FFmpeg
skip_ffmpeg = False
if ffmpeg_dir.exists():
    confirm = input("FFmpeg folder exists. Update it? (y/n): ").strip().lower()
    if confirm == "y":
        shutil.rmtree(ffmpeg_dir)
    else:
        skip_ffmpeg = True

if not skip_ffmpeg:
    ffmpeg_dir.mkdir(exist_ok=True)
    if download_file("https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z", ffmpeg_zip):
        print("Extract ffmpeg-git-full.7z to C:/ffmpeg")
        subprocess.run(f'explorer "{ffmpeg_dir}"')
        yn = input("Have you extracted it? (y/n): ").strip().lower()
        if yn == "y":
            target_bin = next(ffmpeg_dir.rglob("*/bin"), None)
            if target_bin:
                add_to_user_path(str(target_bin))
        try:
            ffmpeg_zip.unlink()
        except: pass

# 5. Download updater
try:
    updater_path = user_profile / "updater.py"
    urlretrieve(f"{repo_base}/Updater.py", updater_path)
    print(f"Downloaded updater.py to {updater_path}")
except Exception as e:
    print(f"Failed to download updater.py: {e}")

# 6. Startup Shortcuts
create_shortcut(
    "Downloader AHK",
    str(project_folder / "Downloader.ahk")
)

create_shortcut(
    "Ytlink Server",
    "cmd.exe",
    f'/c start "" python "{project_folder / "ytlinkserver.py"}"',
    str(project_folder)
)

# 7. Delete self
try:
    Path(__file__).unlink()
    print("Deleted installer script.")
except:
    print("Failed to delete self.")

print("Update complete!")

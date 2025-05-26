import os
import subprocess
import time
import shutil
from pathlib import Path
from urllib.request import urlretrieve
import winreg

print("== Yt-dlp Updater ==")

# Auto detect user folders
user_profile = Path.home()
project_folder = user_profile / "Yt-dlp downloader"
ext_dir = project_folder / "extension_files"
yt_dlp_dir = Path("C:/yt-dlp")
ffmpeg_dir = Path("C:/ffmpeg")
ytlink_path = user_profile / "OneDrive" / "Documentos" / "ytlink.txt"
repo_base = "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main"

files = ["Download.ahk", "ytlinkserver.py", "README.md"]
extension_files = ["content.js", "icon128.png", "icon48.png", "manifest.json"]
ffmpeg_zip = ffmpeg_dir / "ffmpeg-git-full.7z"

def download_file(url, dest):
    try:
        urlretrieve(url, dest)
        print(f"Downloaded {os.path.basename(dest)}")
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

def run_installer(installer_path):
    print("Running AutoHotkey installer, please complete installation...")
    subprocess.run([str(installer_path)], check=False)
    print("AutoHotkey installer finished or closed.")
    for attempt in range(5):
        try:
            installer_path.unlink()
            print("Deleted AutoHotkey installer.")
            break
        except Exception as e:
            print(f"Could not delete AutoHotkey installer, retrying... ({e})")
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
        print(f"Added {new_path} to user PATH.")
        print("Log off or restart to apply PATH changes.")
    else:
        print(f"{new_path} already in user PATH.")

def ahk_installed():
    for path in os.environ["PATH"].split(";"):
        if Path(path.strip('"')) / "AutoHotkey.exe" in Path(path).glob("AutoHotkey.exe"):
            return True
    return False

# Make directories and ytlink.txt
project_folder.mkdir(parents=True, exist_ok=True)
ext_dir.mkdir(exist_ok=True)
ytlink_path.parent.mkdir(parents=True, exist_ok=True)
ytlink_path.touch(exist_ok=True)

# 1. AHK
ahk_installer = project_folder / "AutoHotkey_Installer.exe"
if not ahk_installed():
    if download_file("https://www.autohotkey.com/download/ahk-v2.exe", ahk_installer):
        run_installer(ahk_installer)
    else:
        print("Failed to download AutoHotkey installer. Please install manually.")
else:
    print("AutoHotkey already installed.")

# 2. Download all script files
for file in files:
    download_file(f"{repo_base}/{file}", project_folder / file)
for file in extension_files:
    download_file(f"{repo_base}/{file}", ext_dir / file)

# 3. yt-dlp
if yt_dlp_dir.exists():
    confirm = input("yt-dlp folder exists. Update it? (y/n): ").strip().lower()
    if confirm == "y":
        shutil.rmtree(yt_dlp_dir)
        print("yt-dlp folder removed.")
yt_dlp_dir.mkdir(exist_ok=True)
yt_dlp_path = yt_dlp_dir / "yt-dlp.exe"
if download_file("https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe", yt_dlp_path):
    add_to_user_path(str(yt_dlp_dir))

# 4. FFmpeg
if ffmpeg_dir.exists():
    confirm = input("FFmpeg folder exists. Update it? (y/n): ").strip().lower()
    if confirm == "y":
        shutil.rmtree(ffmpeg_dir)
        ffmpeg_dir.mkdir()
        print("FFmpeg folder removed.")
ffmpeg_dir.mkdir(exist_ok=True)

if download_file("https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z", ffmpeg_zip):
    print("Please extract ffmpeg-git-full.7z to C:/ffmpeg")
    subprocess.run(f'explorer "{ffmpeg_dir}"')
    yn = input("Have you extracted it? (y/n): ").strip().lower()
    if yn == "y":
        target_bin = Path("C:/ffmpeg/ffmpeg-git-full/ffmpeg-2025-05-26-git-43a69886b2-full_build/bin")
        if target_bin.exists():
            add_to_user_path(str(target_bin))
        else:
            print("Could not find expected bin folder at:", target_bin)
    try:
        ffmpeg_zip.unlink()
        print("Deleted FFmpeg archive.")
    except Exception as e:
        print(f"Couldn't delete FFmpeg archive: {e}")
else:
    print("Failed to download FFmpeg archive.")

# 5. Rename script to update.py and delete old
script_path = Path(__file__)
if script_path.name.lower() != "update.py":
    new_path = script_path.with_name("update.py")
    shutil.copy(script_path, new_path)
    print("Copied script to update.py")
    try:
        script_path.unlink()
        print("Deleted original install script.")
    except Exception as e:
        print(f"Could not delete original script: {e}")

print("Update complete!")

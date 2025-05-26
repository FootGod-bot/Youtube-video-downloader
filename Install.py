import os
import requests
import subprocess
import time
from pathlib import Path
from urllib.request import urlretrieve
import shutil
import winreg

print("== Yt-dlp Downloader Updater ==")

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
    else:
        print("Skipping delete of AutoHotkey installer after multiple attempts.")

def add_to_user_path(new_path):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment', 0, winreg.KEY_READ) as key:
            existing_path, _ = winreg.QueryValueEx(key, "PATH")
    except FileNotFoundError:
        existing_path = ""

    if new_path.lower() not in existing_path.lower():
        updated_path = existing_path + ";" + new_path if existing_path else new_path
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment', 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, updated_path)
            print(f"Added {new_path} to user PATH.")
            print("Log off or restart to apply PATH changes.")
        except Exception as e:
            print(f"Error updating user PATH: {e}")
    else:
        print(f"{new_path} already in user PATH.")

def is_ahk_installed():
    try:
        subprocess.run(["AutoHotkey.exe", "/ErrorStdOut"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

project_folder = Path(r"C:\Users\aiden\Yt-dlp downloader")
project_folder.mkdir(parents=True, exist_ok=True)

ext_dir = project_folder / "extension_files"
ext_dir.mkdir(exist_ok=True)

repo_base = "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main"

files = [
    "Download.ahk", "ytlinkserver.py", "Download.exe", "README.md"
]

extension_files = [
    "content.js", "icon128.png", "icon48.png", "manifest.json"
]

# 1. AutoHotkey check and install
ahk_installer = project_folder / "AutoHotkey_Installer.exe"
if not is_ahk_installed():
    if download_file("https://www.autohotkey.com/download/ahk-v2.exe", ahk_installer):
        run_installer(ahk_installer)
    else:
        print("Failed to download AutoHotkey installer. Please install manually.")
else:
    print("AutoHotkey is already installed.")

# 2. Main files
for file in files:
    download_file(f"{repo_base}/{file}", project_folder / file)

# 3. Extension files
for file in extension_files:
    download_file(f"{repo_base}/{file}", ext_dir / file)

# 4. yt-dlp install
yt_dlp_dir = Path("C:/yt-dlp")
yt_dlp_dir.mkdir(exist_ok=True)
yt_dlp_path = yt_dlp_dir / "yt-dlp.exe"
if not yt_dlp_path.exists():
    if download_file("https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe", yt_dlp_path):
        add_to_user_path(str(yt_dlp_dir))
else:
    print("yt-dlp already exists.")

# 5. FFmpeg install
ffmpeg_dir = Path("C:/ffmpeg")
ffmpeg_dir.mkdir(exist_ok=True)
ffmpeg_7z = ffmpeg_dir / "ffmpeg-git-full.7z"
bin_added = False

if not any((subdir / "bin").exists() for subdir in ffmpeg_dir.iterdir() if subdir.is_dir()):
    if not ffmpeg_7z.exists():
        if download_file("https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z", ffmpeg_7z):
            print(f"FFmpeg archive downloaded to: {ffmpeg_7z}")
    print("Please extract the 7z archive manually into C:\\ffmpeg")
    yn = input("Have you extracted it? (y/n): ").lower()
    if yn == "y":
        for subfolder in ffmpeg_dir.iterdir():
            bin_path = subfolder / "bin"
            if bin_path.exists():
                add_to_user_path(str(bin_path))
                bin_added = True
                break
        if not bin_added:
            print("FFmpeg bin folder not found.")
else:
    print("FFmpeg appears to be already extracted.")
    for subfolder in ffmpeg_dir.iterdir():
        bin_path = subfolder / "bin"
        if bin_path.exists():
            add_to_user_path(str(bin_path))
            break

print("Update complete! Reload extension or restart apps if needed.")

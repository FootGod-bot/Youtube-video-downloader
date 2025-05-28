import os
import subprocess
import sys
import time
import urllib.request
import zipfile
import shutil
import ctypes
from pathlib import Path

print("== Yt-dlp Installer ==")

user_home = str(Path.home())
download_dir = os.path.join(user_home, "Yt-dlp_downloader")
os.makedirs(download_dir, exist_ok=True)
os.chdir(download_dir)

ahk_v1_path = Path(user_home) / "AppData/Local/Programs/AutoHotkey/v1.1.37.02/AutoHotkeyU64.exe"
if not ahk_v1_path.exists():
    ahk_installer_url = "https://www.autohotkey.com/download/ahk-v2.exe"
    ahk_installer_path = Path("AutoHotkey_Installer.exe")
    urllib.request.urlretrieve(ahk_installer_url, ahk_installer_path)
    print("Downloaded AutoHotkey_Installer.exe")
    print("Running AutoHotkey installer...")
    subprocess.run([str(ahk_installer_path)], check=False)
    print("Installer finished.")
    for _ in range(4):
        try:
            ahk_installer_path.unlink()
            print("Deleted installer.")
            break
        except Exception as e:
            print(f"Could not delete installer, retrying... ({e})")
            time.sleep(1)
    if not ahk_v1_path.exists():
        install_ahk_script = Path(user_home) / "AppData/Local/Programs/AutoHotkey/UX/install.ahk"
        if install_ahk_script.exists():
            subprocess.run(["C:/Program Files/AutoHotkey/v2/AutoHotkey64.exe", str(install_ahk_script)], check=False)
else:
    print("AutoHotkey already installed.")

files = [
    ("https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/Downloader.ahk", "Downloader.ahk"),
    ("https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/ytlinkserver.py", "ytlinkserver.py"),
    ("https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/README.md", "README.md"),
    ("https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/extension/content.js", "content.js"),
    ("https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/extension/icon128.png", "icon128.png"),
    ("https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/extension/icon48.png", "icon48.png"),
    ("https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/extension/manifest.json", "manifest.json")
]

for url, filename in files:
    urllib.request.urlretrieve(url, filename)
    print(f"Downloaded {filename}")

yt_dlp_dir = Path("C:/yt-dlp")
if yt_dlp_dir.exists():
    if input("yt-dlp folder exists. Update it? (y/n): ").lower() == 'y':
        shutil.rmtree(yt_dlp_dir)
        print("yt-dlp folder removed.")
    else:
        yt_dlp_dir = None

if yt_dlp_dir is None or not yt_dlp_dir.exists():
    yt_dlp_dir = Path("C:/yt-dlp")
    yt_dlp_dir.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve("https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe", yt_dlp_dir / "yt-dlp.exe")
    print("Downloaded yt-dlp.exe")
    subprocess.run(["setx", "PATH", f"%PATH%;{yt_dlp_dir}"])
    print("Added C:\\yt-dlp to user PATH.")
    print("Log off or restart to apply PATH changes.")

ffmpeg_dir = Path("C:/ffmpeg")
if ffmpeg_dir.exists():
    if input("FFmpeg folder exists. Update it? (y/n): ").lower() == 'y':
        shutil.rmtree(ffmpeg_dir)
        print("FFmpeg folder removed.")
    else:
        ffmpeg_dir = None

if ffmpeg_dir is None or not ffmpeg_dir.exists():
    ffmpeg_zip = "ffmpeg-git-full.7z"
    ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z"
    urllib.request.urlretrieve(ffmpeg_url, ffmpeg_zip)
    print("Downloaded ffmpeg-git-full.7z")
    print("Please extract ffmpeg-git-full.7z to C:/ffmpeg")
    if input("Have you extracted it? (y/n): ").lower() == 'y':
        ffmpeg_bin = Path("C:/ffmpeg/ffmpeg-git-full/ffmpeg-2025-05-26-git-43a69886b2-full_build/bin")
        if ffmpeg_bin.exists():
            subprocess.run(["setx", "PATH", f"%PATH%;{ffmpeg_bin}"])
            print(f"Added {ffmpeg_bin} to user PATH.")
            print("Log off or restart to apply PATH changes.")
        os.remove(ffmpeg_zip)
        print("Deleted FFmpeg archive.")

from win32com.client import Dispatch

def create_shortcut(target, lnk_path, working_dir):
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortcut(str(lnk_path))
    shortcut.TargetPath = str(target)
    shortcut.WorkingDirectory = str(working_dir)
    shortcut.Save()

desktop = Path(os.path.join(os.environ['USERPROFILE'], 'Desktop'))

lnk1 = desktop / "ytlinkserver.lnk"
if lnk1.exists():
    lnk1.unlink()
    print("Deleted existing shortcut: ytlinkserver.lnk")
create_shortcut(Path(download_dir) / "ytlinkserver.py", lnk1, download_dir)
print("Shortcut created: ytlinkserver.lnk")

lnk2 = desktop / "downloader.ahk.lnk"
if lnk2.exists():
    lnk2.unlink()
    print("Deleted existing shortcut: downloader.ahk.lnk")

if ahk_v1_path.exists():
    create_shortcut(ahk_v1_path, lnk2, download_dir)
    print("Shortcut created: downloader.ahk.lnk")
else:
    print("AutoHotkey.exe not found. Cannot create Downloader.ahk shortcut.")

print("Setup complete!")

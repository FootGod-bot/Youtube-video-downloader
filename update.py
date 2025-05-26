import ctypes
import sys
import os
import subprocess
from pathlib import Path
import requests
import getpass
from pathlib import Path

# Detect current user (the user running the script, assumed admin)
INSTALL_USER = getpass.getuser()
DOWNLOAD_DIR = Path(f"C:/Users/{INSTALL_USER}/Yt-dlp downloader")

FFMPEG_FOLDER = Path("C:/ffmpeg")

AUTOHOTKEY_URL = "https://www.autohotkey.com/download/ahk-v2.exe"
SEVENZIP_URL = "https://www.7-zip.org/a/7z2301-x64.exe"
YTDLP_URL = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
FFMPEG_7Z_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z"

EXTENSION_FILES = {
    "content.js": "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/content.js",
    "icon128.png": "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/icon128.png",
    "icon48.png": "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/icon48.png",
    "manifest.json": "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/manifest.json",
}

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def download_file(url, dest_path):
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with open(dest_path, "wb") as f:
            f.write(response.content)
        print(f"Downloaded {dest_path.name}")
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

def add_system_path(path_str):
    import winreg
    path_str = str(path_str)
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 0, winreg.KEY_READ) as key:
            current_path, _ = winreg.QueryValueEx(key, "Path")
    except FileNotFoundError:
        current_path = ""

    if path_str.lower() in [p.lower() for p in current_path.split(";")]:
        print(f"{path_str} already in system PATH.")
        return

    new_path = current_path + ";" + path_str if current_path else path_str
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
        print(f"Added {path_str} to system PATH.")
        print("You need to log off or restart for PATH changes to apply.")
    except Exception as e:
        print(f"Failed to update system PATH: {e}")

def run_installer(path, silent=False):
    try:
        if silent:
            subprocess.run([str(path), "/S"], check=True)
        else:
            subprocess.run([str(path)], check=True)
        return True
    except Exception as e:
        print(f"Failed to run {path.name}: {e}")
        return False

def main():
    if not is_admin():
        print("This script must be run as Administrator!")
        sys.exit(1)

    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    os.chdir(DOWNLOAD_DIR)

    # AutoHotkey
    ahk_path = DOWNLOAD_DIR / "AutoHotkey_Installer.exe"
    if not ahk_path.exists():
        print("Downloading AutoHotkey...")
        download_file(AUTOHOTKEY_URL, ahk_path)
    print("Running AutoHotkey installer...")
    run_installer(ahk_path, silent=False)

    # 7-Zip
    seven_path = DOWNLOAD_DIR / "7zip_installer.exe"
    if not seven_path.exists():
        print("Downloading 7-Zip...")
        download_file(SEVENZIP_URL, seven_path)
    print("Installing 7-Zip...")
    run_installer(seven_path, silent=True)

    # yt-dlp
    ytdlp_path = DOWNLOAD_DIR / "yt-dlp.exe"
    if not ytdlp_path.exists():
        print("Downloading yt-dlp...")
        download_file(YTDLP_URL, ytdlp_path)

    # Extension Files
    for name, url in EXTENSION_FILES.items():
        file_path = DOWNLOAD_DIR / name
        if not file_path.exists():
            print(f"Downloading {name}...")
            download_file(url, file_path)

    # Add yt-dlp folder to system PATH (all users)
    add_system_path(DOWNLOAD_DIR)

    # FFmpeg
    ffmpeg_zip = DOWNLOAD_DIR / "ffmpeg.7z"
    if not ffmpeg_zip.exists():
        print("Downloading FFmpeg 7z archive...")
        download_file(FFMPEG_7Z_URL, ffmpeg_zip)

    print("Extracting FFmpeg...")
    subprocess.run([
        "C:\\Program Files\\7-Zip\\7z.exe",
        "x", str(ffmpeg_zip),
        f"-o{FFMPEG_FOLDER}", "-y"
    ], check=True)

    # Find bin folder inside extracted ffmpeg
    print("Looking for ffmpeg 'bin' folder...")
    subfolders = list(FFMPEG_FOLDER.glob("*_full_build/bin"))
    if subfolders:
        add_system_path(str(subfolders[0]))
    else:
        print("Could not locate ffmpeg/bin folder. Add it manually to PATH if needed.")

    # Cleanup
    for f in [ahk_path, seven_path, ffmpeg_zip]:
        try:
            f.unlink()
            print(f"Deleted {f.name}")
        except:
            print(f"Could not delete {f.name}, delete manually if needed.")

    print("\nInstaller complete! Log off or restart to apply PATH changes.")

if __name__ == "__main__":
    main()

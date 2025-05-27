import os
import sys
import shutil
import subprocess
from pathlib import Path
import urllib.request
import time

print("== Yt-dlp Installer ==")

user_profile = Path(os.environ["USERPROFILE"])
project_folder = user_profile / "Yt-dlp downloader"
project_folder.mkdir(exist_ok=True)

# Helper to download file
def download(url, dest):
    try:
        urllib.request.urlretrieve(url, dest)
        print(f"Downloaded {dest.name}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

# Download AutoHotkey v2 installer and run it
ahk_installer = project_folder / "ahk-v2.exe"
download("https://www.autohotkey.com/download/ahk-v2.exe", ahk_installer)
print("Running AutoHotkey installer, please complete installation...")
subprocess.run([str(ahk_installer)])
try:
    ahk_installer.unlink()
    print("Deleted AutoHotkey installer.")
except PermissionError:
    print("Could not delete AutoHotkey installer, retrying...")
    for _ in range(5):
        time.sleep(1)
        try:
            ahk_installer.unlink()
            print("Deleted AutoHotkey installer.")
            break
        except PermissionError:
            pass

# Download other files
files = {
    "Downloader.ahk": "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/Downloader.ahk",
    "ytlinkserver.py": "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/ytlinkserver.py",
    "README.md": "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/README.md",
    "content.js": "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/content.js",
    "icon128.png": "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/icon128.png",
    "icon48.png": "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/icon48.png",
    "manifest.json": "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/manifest.json",
    "yt-dlp.exe": "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe",
    "updater.py": "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/refs/heads/main/Updater.py",
}

for fname, furl in files.items():
    download(furl, project_folder / fname)

# yt-dlp folder check
yt_dlp_dir = Path("C:/yt-dlp")
if yt_dlp_dir.exists():
    answer = input("yt-dlp folder exists. Update it? (y/n): ").strip().lower()
    if answer == "y":
        print("Updating yt-dlp folder (not implemented here)...")
else:
    print("yt-dlp folder not found, please install manually.")

# ffmpeg folder check
ffmpeg_dir = Path("C:/ffmpeg")
if ffmpeg_dir.exists():
    answer = input("FFmpeg folder exists. Update it? (y/n): ").strip().lower()
    if answer == "y":
        print("Updating FFmpeg folder (not implemented here)...")
else:
    print("FFmpeg folder not found, please extract ffmpeg-git-full.7z to C:/ffmpeg")

# RBTray download & clean
rbtray_dir = project_folder / "RBTray"
if rbtray_dir.exists():
    try:
        shutil.rmtree(rbtray_dir)
        print("Deleted existing RBTray folder.")
    except Exception as e:
        print(f"Failed to delete RBTray folder: {e}")
rbtray_dir.mkdir(parents=True, exist_ok=True)

rbtray_files = {
    "RBTray.exe": "https://raw.githubusercontent.com/benbuck/rbtray/main/x64/RBTray.exe",
    "RBHook.dll": "https://raw.githubusercontent.com/benbuck/rbtray/main/x64/RBHook.dll"
}
for fname, furl in rbtray_files.items():
    download(furl, rbtray_dir / fname)

# Create startup shortcuts
def create_shortcut(target_path, shortcut_name):
    startup_dir = user_profile / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    shortcut_path = startup_dir / f"{shortcut_name}.lnk"
    try:
        import pythoncom
        from win32com.client import Dispatch
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortcut(str(shortcut_path))
        shortcut.TargetPath = str(target_path)
        shortcut.WorkingDirectory = str(target_path.parent)
        shortcut.save()
        print(f"Shortcut created: {shortcut_path}")
    except ImportError:
        print("pywin32 is required to create shortcuts. Please install it with 'pip install pywin32'.")
    except Exception as e:
        print(f"Failed to create shortcut {shortcut_name}: {e}")

create_shortcut(project_folder / "Downloader.ahk", "Downloader")
create_shortcut(project_folder / "ytlinkserver.py", "ytlinkserver")
create_shortcut(rbtray_dir / "RBTray.exe", "RBTray")

print("Launching Downloader.ahk, ytlinkserver.py, and RBTray.exe...")

# Run .ahk like double-click
try:
    os.startfile(str(project_folder / "Downloader.ahk"))
except Exception as e:
    print(f"Failed to run Downloader.ahk via double-click: {e}")

# Run Flask server in new console window
try:
    subprocess.Popen([sys.executable, str(project_folder / "ytlinkserver.py")], creationflags=subprocess.CREATE_NEW_CONSOLE)
except Exception as e:
    print(f"Failed to run ytlinkserver.py: {e}")

# Run RBTray
try:
    subprocess.Popen([str(rbtray_dir / "RBTray.exe")])
except Exception as e:
    print(f"Failed to run RBTray.exe: {e}")

# Delete this script after running
try:
    os.remove(__file__)
    print("Deleted installer script.")
except Exception:
    pass

print("Install complete!")

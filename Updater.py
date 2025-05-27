import os
import sys
import shutil
import subprocess
from pathlib import Path
import urllib.request

print("== Yt-dlp Installer ==")

user_profile = Path(os.environ["USERPROFILE"])
project_folder = user_profile / "Yt-dlp downloader"
extension_folder = project_folder / "extension"
rbtray_dir = project_folder / "RBTray"
updater_dest = user_profile / "updater.py"

project_folder.mkdir(exist_ok=True)
extension_folder.mkdir(exist_ok=True)
rbtray_dir.mkdir(exist_ok=True)

def download(url, dest):
    try:
        urllib.request.urlretrieve(url, dest)
        print(f"Downloaded {dest.name}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

# Download and run AutoHotkey installer
ahk_installer = project_folder / "ahk-v2.exe"
download("https://www.autohotkey.com/download/ahk-v2.exe", ahk_installer)
print("Running AutoHotkey installer, please complete installation...")
subprocess.run([str(ahk_installer)])
try:
    ahk_installer.unlink()
except:
    print("Could not delete AutoHotkey installer.")

# Downloader scripts and others
main_files = {
    "Downloader.ahk": "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/Downloader.ahk",
    "ytlinkserver.py": "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/ytlinkserver.py",
    "README.md": "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/README.md",
}
for fname, url in main_files.items():
    download(url, project_folder / fname)

# Extension files
extension_files = {
    "content.js": "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/content.js",
    "icon128.png": "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/icon128.png",
    "icon48.png": "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/icon48.png",
    "manifest.json": "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/manifest.json",
}
for fname, url in extension_files.items():
    download(url, extension_folder / fname)

# Ask to download yt-dlp.exe
yt_dlp_path = project_folder / "yt-dlp.exe"
if Path("C:/yt-dlp").exists():
    answer = input("yt-dlp folder exists. Update it? (y/n): ").strip().lower()
    if answer == "y":
        download("https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe", yt_dlp_path)

# Ask about FFmpeg
if Path("C:/ffmpeg").exists():
    answer = input("FFmpeg folder exists. Update it? (y/n): ").strip().lower()
    if answer == "y":
        print("Update FFmpeg manually (not implemented).")
else:
    print("FFmpeg folder not found, please extract ffmpeg-git-full.7z to C:/ffmpeg")

# RBTray
for fname in ["RBTray.exe", "RBHook.dll"]:
    url = f"https://raw.githubusercontent.com/benbuck/rbtray/main/x64/{fname}"
    download(url, rbtray_dir / fname)

# updater.py
download("https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/updater.py", updater_dest)

# Shortcuts
def create_shortcut(target_path, shortcut_name):
    try:
        import pythoncom
        from win32com.client import Dispatch
        startup = user_profile / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"
        shortcut_path = startup / f"{shortcut_name}.lnk"
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortcut(str(shortcut_path))
        shortcut.TargetPath = str(target_path)
        shortcut.WorkingDirectory = str(target_path.parent)
        shortcut.save()
        print(f"Shortcut created: {shortcut_path}")
    except:
        print(f"Failed to create shortcut for {shortcut_name}. Install pywin32 if needed.")

create_shortcut(project_folder / "Downloader.ahk", "Downloader")
create_shortcut(project_folder / "ytlinkserver.py", "ytlinkserver")
create_shortcut(rbtray_dir / "RBTray.exe", "RBTray")

# Launch scripts
print("Launching Downloader.ahk, ytlinkserver.py, and RBTray.exe...")
try:
    os.startfile(str(project_folder / "Downloader.ahk"))
except Exception as e:
    print(f"Couldn't launch .ahk: {e}")

try:
    subprocess.Popen([sys.executable, str(project_folder / "ytlinkserver.py")], creationflags=subprocess.CREATE_NEW_CONSOLE)
except Exception as e:
    print(f"Couldn't launch ytlinkserver: {e}")

try:
    subprocess.Popen([str(rbtray_dir / "RBTray.exe")])
except Exception as e:
    print(f"Couldn't launch RBTray: {e}")

# Delete self
try:
    os.remove(__file__)
except:
    pass

print("Install complete!")

import os
import sys
import shutil
import subprocess
from pathlib import Path
import urllib.request
import time
import winreg

print("== Yt-dlp Installer ==")

user_profile = Path(os.environ["USERPROFILE"])
project_folder = user_profile / "Yt-dlp downloader"
project_folder.mkdir(exist_ok=True)

def download(url, dest):
    try:
        urllib.request.urlretrieve(url, dest)
        print(f"Downloaded {dest.name}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

def find_autohotkey_exe():
    # Check common install locations
    common_paths = [
        Path("C:/Program Files/AutoHotkey/AutoHotkey.exe"),
        Path("C:/Program Files (x86)/AutoHotkey/AutoHotkey.exe"),
        user_profile / "AppData" / "Local" / "Programs" / "AutoHotkey" / "AutoHotkey.exe",
    ]
    for path in common_paths:
        if path.is_file():
            return path

    # Try registry (64-bit or 32-bit)
    try:
        for hive in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
            try:
                reg_key = winreg.OpenKey(hive, r"SOFTWARE\AutoHotkey")
            except FileNotFoundError:
                continue
            exe_path, _ = winreg.QueryValueEx(reg_key, "ExePath")
            if exe_path and Path(exe_path).is_file():
                return Path(exe_path)
    except Exception:
        pass

    return None

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

# Download other files (use your real URLs here)
files = {
    "Downloader.ahk": "https://raw.githubusercontent.com/yourrepo/Downloader.ahk",
    "ytlinkserver.py": "https://raw.githubusercontent.com/yourrepo/ytlinkserver.py",
    "README.md": "https://raw.githubusercontent.com/yourrepo/README.md",
    "content.js": "https://raw.githubusercontent.com/yourrepo/content.js",
    "icon128.png": "https://raw.githubusercontent.com/yourrepo/icon128.png",
    "icon48.png": "https://raw.githubusercontent.com/yourrepo/icon48.png",
    "manifest.json": "https://raw.githubusercontent.com/yourrepo/manifest.json",
    "yt-dlp.exe": "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe",
    "updater.py": "https://raw.githubusercontent.com/yourrepo/updater.py",
}

for fname, furl in files.items():
    download(furl, project_folder / fname)

# RBTray download & clean old folder
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

# Create Startup shortcuts function
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
        print("pywin32 required for shortcuts. Run: python -m pip install pywin32")
    except Exception as e:
        print(f"Failed to create shortcut {shortcut_name}: {e}")

create_shortcut(project_folder / "Downloader.ahk", "Downloader")
create_shortcut(project_folder / "ytlinkserver.py", "ytlinkserver")
create_shortcut(rbtray_dir / "RBTray.exe", "RBTray")

# Find AutoHotkey.exe
ahk_exe = find_autohotkey_exe()
if not ahk_exe:
    print("AutoHotkey.exe not found. Please install AutoHotkey and ensure it's installed correctly.")
else:
    print(f"Found AutoHotkey.exe at {ahk_exe}")

# Launch Downloader.ahk using AutoHotkey.exe with the script path as argument
if ahk_exe:
    try:
        subprocess.Popen([str(ahk_exe), str(project_folder / "Downloader.ahk")])
        print("Launched Downloader.ahk with AutoHotkey.exe")
    except Exception as e:
        print(f"Failed to launch Downloader.ahk: {e}")

# Launch Flask server in new console window
try:
    subprocess.Popen([sys.executable, str(project_folder / "ytlinkserver.py")], creationflags=subprocess.CREATE_NEW_CONSOLE)
    print("Launched ytlinkserver.py in a new console window")
except Exception as e:
    print(f"Failed to launch ytlinkserver.py: {e}")

# Launch RBTray
try:
    subprocess.Popen([str(rbtray_dir / "RBTray.exe")])
    print("Launched RBTray.exe")
except Exception as e:
    print(f"Failed to launch RBTray.exe: {e}")

print("Install complete!")

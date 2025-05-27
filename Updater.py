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
repo_base = "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main"

files = ["Downloader.ahk", "ytlinkserver.py", "README.md"]
extension_files = ["content.js", "icon128.png", "icon48.png", "manifest.json"]
ffmpeg_zip = ffmpeg_dir / "ffmpeg-git-full.7z"

# Helpers
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
    for path in os.environ.get("PATH", "").split(";"):
        if Path(path.strip('"')) / "AutoHotkey.exe" in Path(path).glob("AutoHotkey.exe"):
            return True
    return False

def find_ahk_exe():
    candidates = [
        os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "AutoHotkey", "AutoHotkey.exe"),
        os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "AutoHotkey", "AutoHotkey.exe"),
        os.path.join(str(user_profile), "AppData", "Local", "Programs", "AutoHotkey", "AutoHotkey.exe"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None

def create_shortcut(target, shortcut_path, description=""):
    import pythoncom
    from win32com.shell import shell, shellcon
    from win32com.client import Dispatch

    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortcut(str(shortcut_path))
    shortcut.TargetPath = str(target)
    shortcut.WorkingDirectory = str(target.parent)
    shortcut.Description = description
    shortcut.Save()
    print(f"Shortcut created: {shortcut_path}")

# Prepare folders
project_folder.mkdir(parents=True, exist_ok=True)
ext_dir.mkdir(exist_ok=True)
ytlink_path.parent.mkdir(parents=True, exist_ok=True)
ytlink_path.touch(exist_ok=True)

# 1. Install AutoHotkey if missing
ahk_installer = project_folder / "AutoHotkey_Installer.exe"
if not ahk_installed():
    if download_file("https://www.autohotkey.com/download/ahk-v2.exe", ahk_installer):
        run_installer(ahk_installer)
    else:
        print("Failed to download AutoHotkey installer. Please install manually.")
else:
    print("AutoHotkey already installed.")

# 2. Download scripts & extension files
for file in files:
    download_file(f"{repo_base}/{file}", project_folder / file)
for file in extension_files:
    download_file(f"{repo_base}/{file}", ext_dir / file)

# 3. Download or update yt-dlp
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
    if download_file("https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe", yt_dlp_path):
        add_to_user_path(str(yt_dlp_dir))

# 4. Download or update FFmpeg
skip_ffmpeg = False
if ffmpeg_dir.exists():
    confirm = input("FFmpeg folder exists. Update it? (y/n): ").strip().lower()
    if confirm == "y":
        shutil.rmtree(ffmpeg_dir)
        print("FFmpeg folder removed.")
    else:
        skip_ffmpeg = True

if not skip_ffmpeg:
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

# 5. Download RBTray files
rbtray_dir = project_folder / "RBTray"
rbtray_dir.mkdir(parents=True, exist_ok=True)
rbtray_files = {
    "RBTray.exe": "https://raw.githubusercontent.com/benbuck/rbtray/main/x64/RBTray.exe",
    "RBHook.dll": "https://raw.githubusercontent.com/benbuck/rbtray/main/x64/RBHook.dll"
}
for filename, url in rbtray_files.items():
    dest_path = rbtray_dir / filename
    download_file(url, dest_path)

# 6. Download updater.py to user profile
try:
    updater_url = f"{repo_base}/Updater.py"
    updater_path = user_profile / "updater.py"
    urlretrieve(updater_url, updater_path)
    print(f"Downloaded updater.py to: {updater_path}")
except Exception as e:
    print(f"Failed to download updater.py: {e}")

# 7. Create Startup shortcuts for Downloader.ahk, ytlinkserver.py, RBTray.exe
startup_folder = user_profile / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
startup_folder.mkdir(exist_ok=True)

try:
    import pythoncom
    from win32com.shell import shell, shellcon
    from win32com.client import Dispatch

    ahk_path = project_folder / "Downloader.ahk"
    ytlinkserver_path = project_folder / "ytlinkserver.py"
    rbtray_exe_path = rbtray_dir / "RBTray.exe"

    create_shortcut(ahk_path, startup_folder / "Downloader.lnk", "Run Downloader AHK script")
    create_shortcut(ytlinkserver_path, startup_folder / "ytlinkserver.lnk", "Run ytlinkserver Python script")
    create_shortcut(rbtray_exe_path, startup_folder / "RBTray.lnk", "Run RBTray")

except ImportError:
    print("pywin32 not installed; skipping shortcut creation. You can manually add these to startup.")

# 8. Launch Downloader.ahk, ytlinkserver.py, RBTray.exe now
def launch_apps():
    ahk_exe = find_ahk_exe()
    if ahk_exe is None:
        print("AutoHotkey.exe not found. Please install AutoHotkey manually to run scripts.")
    else:
        subprocess.Popen([ahk_exe, str(project_folder / "Downloader.ahk")])
    subprocess.Popen([sys.executable, str(project_folder / "ytlinkserver.py")])
    subprocess.Popen([str(rbtray_dir / "RBTray.exe")])
    print("Launched Downloader.ahk, ytlinkserver.py, and RBTray.exe.")

launch_apps()

# 9. Delete installer script if named install.py
script_path = Path(__file__)
if script_path.name.lower() == "updater.py":
    try:
        os.remove(script_path)
        print("Deleted install.py")
    except Exception as e:
        print(f"Could not delete install.py: {e}")

print("Install complete!")

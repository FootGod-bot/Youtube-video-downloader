import os
import subprocess
import time
import shutil
from pathlib import Path
from urllib.request import urlretrieve
import winreg
import sys

print("== Yt-dlp Installer ==")

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

# Create required folders
project_folder.mkdir(parents=True, exist_ok=True)
ext_dir.mkdir(exist_ok=True)
ytlink_path.parent.mkdir(parents=True, exist_ok=True)
ytlink_path.touch(exist_ok=True)

# 1. Install AutoHotkey
ahk_installer = project_folder / "AutoHotkey_Installer.exe"
if not ahk_installed():
    if download_file("https://www.autohotkey.com/download/ahk-v2.exe", ahk_installer):
        run_installer(ahk_installer)
    else:
        print("Failed to download AutoHotkey installer. Please install manually.")
else:
    print("AutoHotkey already installed.")

# 2. Download scripts
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
        print("yt-dlp folder removed.")
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

# 5. Download Updater.py (use fixed URL)
try:
    updater_url = "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main/Updater.py"
    updater_path = user_profile / "updater.py"
    urlretrieve(updater_url, updater_path)
    print(f"Downloaded updater.py to: {updater_path}")
except Exception as e:
    print(f"Failed to download updater.py: {e}")

# 6. Add to startup
def create_shortcut(name, target, args="", open_new_window=False):
    lnk_path = startup_dir / f"{name}.lnk"
    if lnk_path.exists():
        lnk_path.unlink()
    script = f'''
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{lnk_path}")
$Shortcut.TargetPath = "{target}"
$Shortcut.Arguments = "{args}"
$Shortcut.WorkingDirectory = "{project_folder}"
$Shortcut.WindowStyle = 1
$Shortcut.IconLocation = "{target},0"
$Shortcut.Save()
'''
    if open_new_window:
        args = f'/c start cmd /k "python {project_folder / "ytlinkserver.py"}"'
        subprocess.run(["powershell", "-Command", f'Start-Process cmd -ArgumentList \'{args}\''], shell=True)
    else:
        subprocess.run(["powershell", "-Command", script])

# .ahk like double-clicking
create_shortcut("Downloader AHK", str(project_folder / "Downloader.ahk"))

# server in new terminal window
create_shortcut("Ytlink Server", "cmd.exe", f'/c start python "{project_folder / "ytlinkserver.py"}"', open_new_window=True)

# 7. Delete this installer
script_path = Path(__file__)
try:
    os.remove(script_path)
    print("Deleted install.py")
except Exception as e:
    print(f"Could not delete install.py: {e}")

print("Update complete!")

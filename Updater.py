import os
import subprocess
import time
import shutil
from pathlib import Path
from urllib.request import urlretrieve
import winreg

print("== Yt-dlp Installer ==")

# Define key paths
user_profile = Path.home()
project_folder = user_profile / "Yt-dlp downloader"
startup_dir = user_profile / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
ext_dir = project_folder / "extension_files"
yt_dlp_dir = Path("C:/yt-dlp")
ffmpeg_dir = Path("C:/ffmpeg")
ytlink_path = user_profile / "OneDrive" / "Documentos" / "ytlink.txt"
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
        print(f"Added {new_path} to PATH. Restart/log off to apply.")
    else:
        print(f"{new_path} already in user PATH.")

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

    target = str(target).replace('"', '""')
    args = args.replace('"', '""')
    working_dir = str(working_dir or os.path.dirname(target)).replace('"', '""')

    script = f'''
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{path}")
$Shortcut.TargetPath = "{target}"
$Shortcut.Arguments = "{args}"
$Shortcut.WorkingDirectory = "{working_dir}"
$Shortcut.Save()
'''
    subprocess.run(["powershell", "-NoProfile", "-Command", script])

# Create directories
project_folder.mkdir(parents=True, exist_ok=True)
ext_dir.mkdir(exist_ok=True)
ytlink_path.parent.mkdir(parents=True, exist_ok=True)
ytlink_path.touch(exist_ok=True)
startup_dir.mkdir(parents=True, exist_ok=True)

# 1. AHK
ahk_installer = project_folder / "AutoHotkey_Installer.exe"
if not ahk_installed():
    if download_file("https://www.autohotkey.com/download/ahk-v2.exe", ahk_installer):
        run_installer(ahk_installer)
    else:
        print("AutoHotkey installer failed.")

# 2. Downloader + Server + Readme
for file in files:
    download_file(f"{repo_base}/{file}", project_folder / file)

# 3. Extension files
for file in extension_files:
    download_file(f"{repo_base}/{file}", ext_dir / file)

# 4. yt-dlp
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
    if download_file("https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe", yt_dlp_dir / "yt-dlp.exe"):
        add_to_user_path(str(yt_dlp_dir))

# 5. FFmpeg
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
        print("Extract ffmpeg-git-full.7z to C:/ffmpeg")
        subprocess.run(f'explorer "{ffmpeg_dir}"')
        yn = input("Have you extracted it? (y/n): ").strip().lower()
        if yn == "y":
            target_bin = Path("C:/ffmpeg/ffmpeg-git-full/ffmpeg-2025-05-26-git-43a69886b2-full_build/bin")
            if target_bin.exists():
                add_to_user_path(str(target_bin))
        try:
            ffmpeg_zip.unlink()
        except: pass

# 6. updater.py
updater_path = user_profile / "updater.py"
if download_file(f"{repo_base}/Updater.py", updater_path):
    print(f"Downloaded updater.py to {updater_path}")

# 7. Shortcuts to Startup
create_shortcut(
    "Ytlink Server",
    "cmd.exe",
    f'/c start "" python "{project_folder / "ytlinkserver.py"}"',
    str(project_folder)
)

create_shortcut(
    "Download AHK",
    str(project_folder / "Downloader.ahk"),
    "",
    str(project_folder)
)

# 8. Delete self if named install.py
try:
    script_path = Path(__file__)
    script_path.unlink()
    print("Deleted installer script.")
except Exception as e:
    print(f"Could not delete self: {e}")

print("Update complete!")

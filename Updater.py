import os
import subprocess
import time
import shutil
import winreg
import sys
import pythoncom
from win32com.shell import shell, shellcon
from pathlib import Path
from urllib.request import urlretrieve

print("== Yt-dlp Updater ==")

# Auto detect user folders
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

def create_shortcut(target_path, shortcut_name, arguments="", start_in=None):
    startup_dir = Path(shell.SHGetFolderPath(0, shellcon.CSIDL_STARTUP, None, 0))
    shortcut_path = startup_dir / f"{shortcut_name}.lnk"

    shell_link = pythoncom.CoCreateInstance(
        shell.CLSID_ShellLink, None,
        pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink
    )
    shell_link.SetPath(str(target_path))
    if arguments:
        shell_link.SetArguments(arguments)
    if start_in:
        shell_link.SetWorkingDirectory(str(start_in))
    persist_file = shell_link.QueryInterface(pythoncom.IID_IPersistFile)
    persist_file.Save(str(shortcut_path), 0)
    print(f"Shortcut created: {shortcut_path}")

# Setup folders and file
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

# 5. Download RBTray
rbtray_dir = project_folder / "RBTray"
rbtray_dir.mkdir(parents=True, exist_ok=True)

rbtray_files = {
    "RBTray.exe": "https://raw.githubusercontent.com/benbuck/rbtray/main/x64/RBTray.exe",
    "RBHook.dll": "https://raw.githubusercontent.com/benbuck/rbtray/main/x64/RBHook.dll"
}

for filename, url in rbtray_files.items():
    dest_path = rbtray_dir / filename
    download_file(url, dest_path)

# 6. Download updater.py
try:
    updater_url = f"{repo_base}/Updater.py"
    updater_path = user_profile / "updater.py"
    urlretrieve(updater_url, updater_path)
    print(f"Downloaded updater.py to: {updater_path}")
except Exception as e:
    print(f"Failed to download updater.py: {e}")

# --- Create startup shortcuts for Downloader.ahk and ytlinkserver.py ---

ahk_script = project_folder / "Downloader.ahk"
python_script = project_folder / "ytlinkserver.py"

# Find AutoHotkey.exe path
autohotkey_exe = Path("C:/Program Files/AutoHotkey/AutoHotkey.exe")
if not autohotkey_exe.exists():
    autohotkey_exe = Path("C:/Program Files (x86)/AutoHotkey/AutoHotkey.exe")

if autohotkey_exe.exists():
    create_shortcut(
        target_path=autohotkey_exe,
        shortcut_name="Downloader (AutoHotkey)",
        arguments=f'"{ahk_script}"',
        start_in=project_folder
    )
else:
    print("AutoHotkey.exe not found, cannot create shortcut for Downloader.ahk")

# Create shortcut for ytlinkserver.py using current python interpreter
python_exe = Path(sys.executable)
create_shortcut(
    target_path=python_exe,
    shortcut_name="ytlinkserver",
    arguments=f'"{python_script}"',
    start_in=project_folder
)

# 7. Delete self if named updater.py
script_path = Path(__file__)
if script_path.name.lower() == "updater.py":
    try:
        os.remove(script_path)
        print("Deleted updater.py")
    except Exception as e:
        print(f"Could not delete updater.py: {e}")

print("Update complete!")

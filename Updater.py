import os
import subprocess
import time
import shutil
from pathlib import Path
from urllib.request import urlretrieve
import winreg
import sys
import pythoncom
import win32com.client

print("== Yt-dlp Installer ==")

user_profile = Path.home()
project_folder = user_profile / "Yt-dlp_downloader"  # no spaces to avoid path issues
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
    for attempt in range(5):
        try:
            installer_path.unlink()
            print("Deleted installer.")
            break
        except Exception as e:
            print(f"Could not delete installer, retrying... ({e})")
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
        if (Path(path.strip('"')) / "AutoHotkey.exe").exists():
            return True
    return False

def create_shortcut(target, arguments, shortcut_path, run_minimized=True):
    pythoncom.CoInitialize()
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(str(shortcut_path))
    shortcut.Targetpath = str(target)
    shortcut.Arguments = arguments
    shortcut.WorkingDirectory = str(Path(target).parent)
    shortcut.WindowStyle = 7 if run_minimized else 1
    shortcut.save()
    print(f"Shortcut created: {shortcut_path.name}")

# Create necessary folders
project_folder.mkdir(parents=True, exist_ok=True)
ext_dir.mkdir(exist_ok=True)
ytlink_path.parent.mkdir(parents=True, exist_ok=True)
ytlink_path.touch(exist_ok=True)

# 1. Install AutoHotkey if not found
ahk_installer = project_folder / "AutoHotkey_Installer.exe"
if not ahk_installed():
    if download_file("https://www.autohotkey.com/download/ahk-v2.exe", ahk_installer):
        run_installer(ahk_installer)
    else:
        print("Failed to download AutoHotkey installer. Please install manually.")
else:
    print("AutoHotkey already installed.")

# 2. Download main files and extension files
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

# 5. Download updater.py again (to self-update)
try:
    updater_url = f"{repo_base}/Updater.py"
    updater_path = user_profile / "updater.py"
    urlretrieve(updater_url, updater_path)
    print(f"Downloaded updater.py to: {updater_path}")
except Exception as e:
    print(f"Failed to download updater.py: {e}")

# --- NEW PART: Run the AHK install-version.ahk and wait for it ---
ahk_install_script = user_profile / "AppData" / "Local" / "Programs" / "AutoHotkey" / "UX" / "install-version.ahk"

if ahk_install_script.exists():
    print(f"Running AHK install script: {ahk_install_script}")
    # Find AutoHotkey Dash exe to run the script
    ahk_exe = None
    dash_paths = [
        user_profile / "AppData" / "Local" / "Programs" / "AutoHotkey" / "UX" / "AutoHotkeyUX.exe",
        Path(r"C:\Program Files\AutoHotkey\UX\AutoHotkeyUX.exe"),
        Path(r"C:\Program Files (x86)\AutoHotkey\UX\AutoHotkeyUX.exe"),
    ]
    for path in dash_paths:
        if path.exists():
            ahk_exe = path
            break
    if not ahk_exe:
        ahk_exe = "AutoHotkey.exe"  # fallback

    proc = subprocess.run([str(ahk_exe), str(ahk_install_script)])
    if proc.returncode == 0:
        print("AHK install script completed successfully.")
    else:
        print(f"AHK install script exited with code {proc.returncode}")
else:
    print(f"AHK install script not found at {ahk_install_script}, skipping.")

# 6. Setup startup shortcuts for ytlinkserver.py and Downloader.ahk

startup_folder = Path(os.getenv('APPDATA')) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"

# Remove existing shortcuts if any
for shortcut_name in ["ytlinkserver.lnk", "downloader.ahk.lnk"]:
    shortcut_path = startup_folder / shortcut_name
    if shortcut_path.exists():
        try:
            shortcut_path.unlink()
            print(f"Deleted existing shortcut: {shortcut_name}")
        except Exception as e:
            print(f"Could not delete existing shortcut {shortcut_name}: {e}")

# Shortcut for ytlinkserver.py (run in new cmd window)
python_exe = sys.executable
ytlinkserver_script = project_folder / "ytlinkserver.py"
ytlinkserver_shortcut = startup_folder / "ytlinkserver.lnk"

create_shortcut(
    target="cmd.exe",
    arguments=f'/c start "" "{python_exe}" "{ytlinkserver_script}"',
    shortcut_path=ytlinkserver_shortcut,
    run_minimized=False
)

# Shortcut for Downloader.ahk (run as double click)

# Find AutoHotkey Dash exe path again for shortcut target
ahk_exe_path = None
for p in os.environ["PATH"].split(";"):
    potential = Path(p.strip('"')) / "AutoHotkey.exe"
    if potential.exists():
        ahk_exe_path = potential
        break

if not ahk_exe_path:
    # fallback to dash exe path checked earlier
    ahk_exe_path = ahk_exe if isinstance(ahk_exe, Path) else None

downloader_ahk = project_folder / "Downloader.ahk"
downloader_shortcut = startup_folder / "downloader.ahk.lnk"

if ahk_exe_path and downloader_ahk.exists():
    create_shortcut(
        target=ahk_exe_path,
        arguments=f'"{downloader_ahk}"',
        shortcut_path=downloader_shortcut,
        run_minimized=True
    )
else:
    print("Cannot create downloader shortcut; AutoHotkey executable or Downloader.ahk not found.")

# 7. Self-delete the installer script after running
import sys

installer_path = Path(sys.argv[0]).resolve()
bat_path = installer_path.with_suffix('.bat')

try:
    with open(bat_path, "w") as f:
        f.write(f"""@echo off
ping 127.0.0.1 -n 5 > nul
del "{installer_path}"
del "%~f0"
""")
    # Run the batch file and detach it
    subprocess.Popen([str(bat_path)], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Created and launched self-delete batch: {bat_path}")
except Exception as e:
    print(f"Failed to create self-delete batch: {e}")


print("Setup complete!")

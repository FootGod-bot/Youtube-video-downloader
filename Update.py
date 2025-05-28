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
project_folder = user_profile / "Yt-dlp_downloader"
ext_dir = project_folder / "extension_files"
yt_dlp_dir = Path("C:/yt-dlp")
ffmpeg_dir = Path("C:/ffmpeg")
ytlink_path = user_profile / "OneDrive" / "Documentos" / "ytlink.txt"
repo_base = "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main"

files = ["Downloader.ahk", "ytlinkserver.py", "README.md"]
extension_files = ["content.js", "icon128.png", "icon48.png", "manifest.json"]
ffmpeg_zip = ffmpeg_dir / "ffmpeg-git-full.7z"

ahk_v1_path = user_profile / "AppData/Local/Programs/AutoHotkey/v1.1.37.02/AutoHotkeyU64.exe"


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


def run_shortcut(shortcut_path):
    try:
        subprocess.Popen(['cmd', '/c', 'start', '', str(shortcut_path)])
        print(f"Started shortcut: {shortcut_path.name}")
    except Exception as e:
        print(f"Failed to start shortcut {shortcut_path.name}: {e}")


def find_ahk_exe():
    paths = [
        user_profile / "AppData/Local/Programs/AutoHotkey/UX/AutoHotkeyUX.exe",
        Path("C:/Program Files/AutoHotkey/UX/AutoHotkeyUX.exe"),
        Path("C:/Program Files (x86)/AutoHotkey/UX/AutoHotkeyUX.exe"),
    ]
    for path in paths:
        if path.exists():
            return path
    return None


ahk_exe_path = find_ahk_exe()
skip_user_script = ahk_v1_path.exists()

project_folder.mkdir(parents=True, exist_ok=True)
ext_dir.mkdir(exist_ok=True)
ytlink_path.parent.mkdir(parents=True, exist_ok=True)
ytlink_path.touch(exist_ok=True)

ahk_installer = project_folder / "AutoHotkey_Installer.exe"
if not ahk_exe_path:
    if download_file("https://www.autohotkey.com/download/ahk-v2.exe", ahk_installer):
        run_installer(ahk_installer)
    else:
        print("Failed to download AutoHotkey installer. Please install manually.")
else:
    print("AutoHotkey already installed.")

for file in files:
    download_file(f"{repo_base}/{file}", project_folder / file)
for file in extension_files:
    download_file(f"{repo_base}/{file}", ext_dir / file)

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
    print("This may take a while...")
    if download_file("https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z", ffmpeg_zip):
        print("Please extract ffmpeg-git-full.7z to C:/ffmpeg")
        subprocess.run(f'explorer "{ffmpeg_dir}"')
        yn = input("Have you extracted it? (y/n): ").strip().lower()
        if yn == "y":
            bin_path = None
            for sub in (ffmpeg_dir / "ffmpeg-git-full").iterdir():
                if sub.is_dir() and "full_build" in sub.name:
                    maybe_bin = sub / "bin"
                    if maybe_bin.exists():
                        bin_path = maybe_bin
                        break
            if bin_path:
                add_to_user_path(str(bin_path))
            else:
                print("Could not find ffmpeg bin folder automatically.")
        try:
            ffmpeg_zip.unlink()
            print("Deleted FFmpeg archive.")
        except Exception as e:
            print(f"Couldn't delete FFmpeg archive: {e}")

if ahk_exe_path and not skip_user_script:
    ahk_user_script = user_profile / "AppData/Local/Programs/AutoHotkey/UX/install-version.ahk"
    if ahk_user_script.exists():
        print(f"Running AHK install script: {ahk_user_script}")
        subprocess.run([str(ahk_exe_path), str(ahk_user_script)], check=False)
        print("AHK install script completed successfully.")

startup_folder = Path(os.getenv('APPDATA')) / "Microsoft/Windows/Start Menu/Programs/Startup"
for shortcut_name in ["ytlinkserver.lnk", "downloader.ahk.lnk"]:
    shortcut_path = startup_folder / shortcut_name
    if shortcut_path.exists():
        try:
            shortcut_path.unlink()
            print(f"Deleted existing shortcut: {shortcut_name}")
        except Exception as e:
            print(f"Could not delete existing shortcut {shortcut_name}: {e}")

python_exe = sys.executable
ytlinkserver_script = project_folder / "ytlinkserver.py"
ytlinkserver_shortcut = startup_folder / "ytlinkserver.lnk"
create_shortcut("cmd.exe", f'/c start "" "{python_exe}" "{ytlinkserver_script}"', ytlinkserver_shortcut, run_minimized=False)
run_shortcut(ytlinkserver_shortcut)

ahk_script = project_folder / "Downloader.ahk"
ahk_shortcut = startup_folder / "downloader.ahk.lnk"
if ahk_v1_path.exists():
    create_shortcut(str(ahk_v1_path), f'"{ahk_script}"', ahk_shortcut, run_minimized=False)
    run_shortcut(ahk_shortcut)
else:
    print("AutoHotkey.exe not found. Cannot create Downloader.ahk shortcut.")

print("Setup complete!")

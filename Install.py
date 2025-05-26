import os
import shutil
import subprocess
import time
from pathlib import Path
from urllib.request import urlretrieve

print("== Yt-dlp Installer ==")

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
    else:
        print("Skipping delete of AutoHotkey installer after multiple attempts.")

def is_ahk_installed():
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\AutoHotkey") as key:
            return True
    except FileNotFoundError:
        return False

def add_to_user_path(new_path):
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment', 0, winreg.KEY_READ) as key:
            existing_path, _ = winreg.QueryValueEx(key, "PATH")
    except FileNotFoundError:
        existing_path = ""

    if new_path.lower() not in existing_path.lower():
        updated_path = existing_path + ";" + new_path if existing_path else new_path
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment', 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, updated_path)
            print(f"Added {new_path} to user PATH.")
            print("Log off or restart to apply PATH changes.")
        except Exception as e:
            print(f"Error updating user PATH: {e}")
    else:
        print(f"{new_path} already in user PATH.")

# Detect current user folder automatically
user_folder = Path.home()
project_folder = user_folder / "Yt-dlp downloader"
project_folder.mkdir(parents=True, exist_ok=True)

ext_dir = project_folder / "extension_files"
ext_dir.mkdir(exist_ok=True)

repo_base = "https://raw.githubusercontent.com/FootGod-bot/Youtube-video-downloader/main"

files = [
    "Download.ahk", "ytlinkserver.py", "Download.exe", "README.md"
]

extension_files = [
    "content.js", "icon128.png", "icon48.png", "manifest.json"
]

# 1. AutoHotkey install check and installer run if needed
ahk_installer = project_folder / "AutoHotkey_Installer.exe"
if not is_ahk_installed():
    print("AutoHotkey not detected. Downloading installer...")
    if download_file("https://www.autohotkey.com/download/ahk-v2.exe", ahk_installer):
        run_installer(ahk_installer)
    else:
        print("Failed to download AutoHotkey installer. Please install manually.")
else:
    print("AutoHotkey already installed.")

# 2. Download main files
for file in files:
    download_file(f"{repo_base}/{file}", project_folder / file)

# 3. Download extension files
for file in extension_files:
    download_file(f"{repo_base}/{file}", ext_dir / file)

# 4. Handle yt-dlp folder and download
yt_dlp_dir = Path("C:/yt-dlp")
update_yt_dlp = True
if yt_dlp_dir.exists():
    print("yt-dlp folder already exists.")
    yn = input("Do you want to update it (delete and re-download)? (y/n): ").lower()
    if yn != "y":
        update_yt_dlp = False
    else:
        shutil.rmtree(yt_dlp_dir)
        yt_dlp_dir.mkdir()
else:
    yt_dlp_dir.mkdir()

if update_yt_dlp:
    yt_dlp_path = yt_dlp_dir / "yt-dlp.exe"
    if download_file("https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe", yt_dlp_path):
        add_to_user_path(str(yt_dlp_dir))

# 5. Handle FFmpeg folder and user prompt
ffmpeg_dir = Path("C:/ffmpeg")
ffmpeg_dir.mkdir(exist_ok=True)
ffmpeg_7z = ffmpeg_dir / "ffmpeg-git-full.7z"

update_ffmpeg = True
if any(ffmpeg_dir.iterdir()):
    print("FFmpeg folder already contains files.")
    yn = input("Do you want to update it (delete and re-download)? (y/n): ").lower()
    if yn != "y":
        update_ffmpeg = False
    else:
        # Remove everything inside ffmpeg_dir (except the 7z file itself)
        for item in ffmpeg_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            elif item.is_file() and item != ffmpeg_7z:
                item.unlink()

if update_ffmpeg:
    if not ffmpeg_7z.exists():
        if not download_file("https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z", ffmpeg_7z):
            print("Failed to download FFmpeg archive.")
    print(f"FFmpeg archive downloaded to: {ffmpeg_7z}")
    print("Please extract it manually using 7-Zip or another tool.")
    subprocess.Popen(f'explorer "{ffmpeg_dir}"')
    yn = input("Have you extracted it to the default folder inside C:\\ffmpeg? (y/n): ").lower()
    if yn == "y":
        found = False
        for subfolder in ffmpeg_dir.iterdir():
            bin_path = subfolder / "bin"
            if bin_path.exists():
                add_to_user_path(str(bin_path))
                found = True
                break
        if not found:
            print("FFmpeg bin folder not found. Make sure you extracted it correctly.")

# 6. Write ytlink.txt in Documents
documents_path = user_folder / "OneDrive" / "Documentos"
documents_path.mkdir(parents=True, exist_ok=True)
ytlink_txt = documents_path / "ytlink.txt"
ytlink_txt.write_text("")

print("Update complete! Reload extension or restart related apps if needed.")

# 7. Rename script to update.py and delete install.py
current_script = Path(__file__)
update_script = current_script.parent / "update.py"
if current_script.name != "update.py":
    try:
        shutil.copy2(current_script, update_script)
        print("Copied script to update.py")
        current_script.unlink()
        print("Deleted original install.py script.")
    except Exception as e:
        print(f"Error renaming script: {e}")

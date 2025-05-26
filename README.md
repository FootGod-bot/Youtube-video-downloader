How to install and use the Yt-dlp downloader with FFmpeg and AutoHotkey
Run the updater script (update.py).

This will download the latest versions of all required files including:

yt-dlp.exe (video downloader)

AutoHotkey_Installer.exe (AutoHotkey installer)

Extension files (content.js, icon128.png, icon48.png, manifest.json)

FFmpeg .7z archive (ffmpeg-git-full.7z)

Install AutoHotkey

The updater runs the AutoHotkey installer automatically.

Complete the installation when prompted.

The script will try to delete the installer afterward. If it can’t, just delete it manually.

Extract FFmpeg manually

The updater downloads the FFmpeg archive (ffmpeg-git-full.7z) to C:\ffmpeg (create this folder if it doesn’t exist).

You must extract the contents of the .7z archive inside the C:\ffmpeg folder.

After extraction, there will be a folder named something like ffmpeg-2025-05-21-git-...-full_build inside C:\ffmpeg.

The full path to the FFmpeg bin folder will look like:

C:\ffmpeg\ffmpeg-2025-05-21-git-4099d53759-full_build\bin
You can extract using tools like 7-Zip or WinRAR.

Tell the updater script you finished extracting FFmpeg

The updater will prompt:

Have you extracted FFmpeg archive to C:\ffmpeg? (y/n):
Type y and press Enter once extraction is complete.

The updater will then add the FFmpeg bin folder path to your user PATH environment variable automatically.

Yt-dlp

yt-dlp.exe is downloaded and placed into C:\yt-dlp.

The updater adds C:\yt-dlp to your user PATH automatically.

Restart or log off

To apply the PATH changes, restart your computer or log off and log back in.

Using the tools

You can now run yt-dlp and ffmpeg commands from any Command Prompt or script.

AutoHotkey scripts will work if you installed AutoHotkey correctly.

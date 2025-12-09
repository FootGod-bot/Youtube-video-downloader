import os
import json
import subprocess
import tkinter as tk
from tkinter import filedialog
import time

# Load config
config_path = os.path.join(os.path.dirname(__file__), "config.json")
with open(config_path, "r") as f:
    config = json.load(f)

STORAGE = config["storage_path"]
os.makedirs(STORAGE, exist_ok=True)

DENO = config.get("deno", False)
COOKIES = config.get("cookies", "")

def detect_txt_files():
    """Return list of .txt files with yt-link first, then queues sorted"""
    files = os.listdir(STORAGE)
    
    yt_links = []
    queues = []
    
    for f in files:
        name, ext = os.path.splitext(f)
        if ext != ".txt":
            continue
        if name == "yt-link":
            yt_links.append(f)
        elif name.startswith("queue"):
            queues.append(f)
    
    # Sort queues numerically by the number after 'queue'
    def queue_sort_key(fname):
        num_part = fname[len("queue") : fname.rfind(".txt")]
        try:
            return int(num_part)
        except ValueError:
            return float('inf')
    
    queues.sort(key=queue_sort_key)
    
    return yt_links + queues


def build_yt_dlp_command(url, is_audio, output_path, is_playlist):
    """Build the yt-dlp command string"""
    cmd_parts = ["yt-dlp"]
    if DENO:
        cmd_parts.append("--js-runtimes deno")
    if COOKIES:
        cmd_parts.append(f'--cookies "{COOKIES}"')
    if is_audio:
        cmd_parts.append("-x --audio-format mp3")
    
    if is_playlist:
        cmd_parts.append(f'-o "{output_path}/%(title)s [%(id)s].%(ext)s"')
    else:
        cmd_parts.append(f'-o "{output_path}"')
    
    cmd_parts.append(f'"{url}"')
    return " ".join(cmd_parts)

def process_file(txt_file):
    txt_path = os.path.join(STORAGE, txt_file)
    with open(txt_path, "r", encoding="utf-8") as f:
        url = f.read().strip()
    
    is_playlist = "/playlist" in url

    # Popup for Audio or Video
    choice = None
    def set_audio():
        nonlocal choice
        choice = True
        root.destroy()
    
    def set_video():
        nonlocal choice
        choice = False
        root.destroy()

    root = tk.Tk()
    root.title(f"Select Format for {txt_file}")
    tk.Label(root, text="Choose format:").pack(padx=20, pady=10)
    tk.Button(root, text="Audio Only", command=set_audio, width=15).pack(pady=5)
    tk.Button(root, text="Video", command=set_video, width=15).pack(pady=5)
    root.mainloop()

    if choice is None:
        print("No choice made, skipping.")
        return

    # File/folder picker automatically based on type
    if is_playlist:
        output_path = filedialog.askdirectory(title="Select output folder for playlist")
        if not output_path:
            print("No folder selected, skipping.")
            return
    else:
        # Get metadata for auto filename
        try:
            result = subprocess.run(
                ["yt-dlp", "-j", url],
                capture_output=True,
                text=True,
                check=True
            )
            metadata = json.loads(result.stdout)
            title = metadata.get("title", "video")
            video_id = metadata.get("id", "")
        except Exception as e:
            print(f"Failed to get video metadata: {e}")
            title = "video"
            video_id = ""
        
        output_path = filedialog.asksaveasfilename(
            title="Select output file (Autofills extension)",
            defaultextension=".%(ext)s",
            initialfile=f"{title} [{video_id}]"
        )
        if not output_path:
            print("No file selected, skipping.")
            return

    # Build command
    cmd = build_yt_dlp_command(url, choice, output_path, is_playlist)

    # Save as .ps1 and remove .txt
    ps1_path = os.path.join(STORAGE, os.path.splitext(txt_file)[0] + ".ps1")
    with open(ps1_path, "w", encoding="utf-8") as f:
        f.write(cmd)

    os.remove(txt_path)
    print(f"Converted {txt_file} → {os.path.basename(ps1_path)}")

def main():
    print("Monitoring storage folder for yt-link / queue files...")
    while True:
        files = detect_txt_files()
        if files:
            for f in files:
                process_file(f)
        time.sleep(1)  # avoid CPU spike

if __name__ == "__main__":
    main()

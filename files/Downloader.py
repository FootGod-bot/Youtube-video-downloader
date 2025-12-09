import os
import subprocess
import time
import json
from winotify import Notification

# Load config
config_path = os.path.join(os.path.dirname(__file__), "config.json")
with open(config_path, "r") as f:
    config = json.load(f)

STORAGE = config["storage_path"]
WIN_MODE = "min"
WATCH = config.get("watch", True)  # default to True if missing

def show_notification(title, msg):
    toast = Notification(app_id="Queue Manager", title=title, msg=msg, duration="long")
    toast.show()

def run_file(filepath):
    """Run a PS1 file according to win-mode. Returns True if success, False if failed."""
    try:
        if WIN_MODE == "hidden":
            completed = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", filepath],
                capture_output=True,
                text=True
            )
        elif WIN_MODE in ("min", "full"):
            completed = subprocess.run(
                ["powershell", "-WindowStyle", WIN_MODE, "-ExecutionPolicy", "Bypass", "-File", filepath]
            )
        return completed.returncode == 0
    except Exception:
        return False

def get_queue_files():
    """Return list of .ps1 queue files sorted numerically."""
    files = []
    for f in os.listdir(STORAGE):
        name, ext = os.path.splitext(f)
        if ext.lower() == ".ps1" and name.startswith("queue"):
            try:
                num = int(name.replace("queue", ""))
                files.append((num, f))
            except:
                continue
    files.sort()
    return [f for _, f in files]

def process_queue():
    while True:
        yt_link_path = os.path.join(STORAGE, "yt-link.ps1")

        # If yt-link.ps1 exists, run it first
        if os.path.exists(yt_link_path):
            while True:
                success = run_file(yt_link_path)
                if success:
                    os.remove(yt_link_path)
                    break
                else:
                    show_notification("Queue Manager", f"Failed to run yt-link.ps1")
                    print("1: Try Again  2: Skip  3: Cancel")
                    choice = input("Enter choice: ").strip()
                    if choice == "1":
                        continue
                    elif choice == "2":
                        os.remove(yt_link_path)
                        break
                    elif choice == "3":
                        print("Exiting.")
                        return
                    else:
                        print("Invalid choice, try again.")

        queue_files = get_queue_files()
        if not queue_files:
            if WATCH:
                time.sleep(1)  # wait and keep monitoring
                continue
            else:
                print("Queue empty. Done.")
                break

        # Promote lowest queue to yt-link.ps1
        next_file = queue_files[0]
        next_name, next_ext = os.path.splitext(next_file)
        promoted_path = os.path.join(STORAGE, "yt-link.ps1")
        orig_path = os.path.join(STORAGE, next_file)
        os.rename(orig_path, promoted_path)

        # Shift all remaining queues up by 1
        for idx, f in enumerate(queue_files[1:], start=1):
            old_path = os.path.join(STORAGE, f)
            old_name, old_ext = os.path.splitext(f)
            new_path = os.path.join(STORAGE, f"queue{idx}.ps1")
            os.rename(old_path, new_path)

        # Run promoted file
        while True:
            success = run_file(promoted_path)
            if success:
                os.remove(promoted_path)
                break
            else:
                show_notification("Queue Manager", f"Failed to run {promoted_path}")
                print("1: Try Again  2: Skip  3: Cancel")
                choice = input("Enter choice: ").strip()
                if choice == "1":
                    continue
                elif choice == "2":
                    os.remove(promoted_path)
                    break
                elif choice == "3":
                    print("Exiting.")
                    return
                else:
                    print("Invalid choice, try again.")

if __name__ == "__main__":
    os.makedirs(STORAGE, exist_ok=True)
    process_queue()

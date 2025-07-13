import os
import time
import tkinter as tk
from tkinter import filedialog

docs = os.path.join(os.path.expanduser("~"), "Documents")

def ask_user_settings():
    result = {"type": None, "path": None}

    def set_choice(choice):
        result["type"] = choice
        win.after(100, choose_folder)  # Call folder dialog after button click

    def choose_folder():
        folder = filedialog.askdirectory(title="Choose save folder")
        if folder:
            result["path"] = folder
        win.destroy()

    win = tk.Tk()
    win.title("Choose Format")
    win.geometry("300x100")
    win.eval('tk::PlaceWindow . center')
    win.resizable(False, False)

    tk.Label(win, text="Choose download type:").pack(pady=10)

    button_frame = tk.Frame(win)
    button_frame.pack()

    tk.Button(button_frame, text="Audio", width=12, command=lambda: set_choice("Audio")).pack(side="left", padx=10)
    tk.Button(button_frame, text="Normal", width=12, command=lambda: set_choice("Normal")).pack(side="right", padx=10)

    win.mainloop()
    return result["type"], result["path"]

def process_temp_file(temp_path, final_path):
    with open(temp_path, "r", encoding="utf-8") as f:
        url = f.read().strip()

    if not url:
        print(f"Skipped empty temp file: {temp_path}")
        os.remove(temp_path)
        return

    format_type, folder = ask_user_settings()
    if not format_type or not folder:
        print("Cancelled by user.")
        return

    formatted = f"Link:{url}\nType:{format_type}\nSavePath:{folder}"

    try:
        with open(final_path, "w", encoding="utf-8") as f:
            f.write(formatted)
        print(f"Formatted and saved to {final_path}")
    except Exception as e:
        print(f"Error saving file: {e}")
        return

    try:
        os.remove(temp_path)
        print(f"Deleted temp file: {temp_path}")
    except Exception as e:
        print(f"Error deleting temp file: {e}")

print("Watching for _temp.txt files in Documents...")

while True:
    temp_files = [f for f in os.listdir(docs) if f.endswith("_temp.txt")]
    for temp_file in temp_files:
        temp_path = os.path.join(docs, temp_file)
        final_path = os.path.join(docs, temp_file.replace("_temp.txt", ".txt"))
        process_temp_file(temp_path, final_path)
    time.sleep(2)

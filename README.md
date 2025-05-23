🎬 YouTube Link Saver – Setup Guide
This tool lets you right-click on a YouTube video and send the link to your computer, where it gets saved to a file. Another tool (like yt-dlp) can then auto-download the video.

🧰 What You’ll Need to Install
You’ll need to install a few tools. Each step below tells you what to do and gives you a download link.

✅ Step 1: Install Python
Go to https://download.python.com

Download the latest version.

Important: When installing, make sure to check the box that says "Add Python to PATH" before you click install.

To check it worked:

Open the Command Prompt

Type: python --version

It should show something like Python 3.12.1

✅ Step 2: Install Flask
This lets your computer run a small local web server.

Open the Command Prompt

Type this and press Enter:

bash
Copy
Edit
pip install flask flask-cors
✅ Step 3: Install yt-dlp
This tool downloads videos.

Go to https://download.yt-dlp.com

Download the yt-dlp.exe file

Put it somewhere easy, like a C:\Tools\yt-dlp\ folder

Add that folder to your System PATH (Google this if unsure)

✅ Step 4: Install FFmpeg
yt-dlp needs this to process video and audio.

Go to https://download.ffmpeg.com

Download the latest version

Extract it to something like C:\Tools\ffmpeg\

Add C:\Tools\ffmpeg\bin to your System PATH

✅ Step 5: Set Up the Python Server
Open Notepad

Copy and paste this code:

python
Copy
Edit
from flask import Flask, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/save', methods=['POST'])
def save_url():
    data = request.get_json()
    url = data.get('url')
    if url:
        file_path = os.path.join(os.path.expanduser("~"), "Documents", "ytlink.txt")
        with open(file_path, "w") as f:
            f.write(url)
        return "OK", 200
    return "Missing URL", 400

if __name__ == "__main__":
    app.run()
Save it as ytlinkserver.py

In Command Prompt, run it with:

bash
Copy
Edit
python ytlinkserver.py
✅ Step 6: Set Up the Browser Extension
Create a folder on your desktop named YouTubeLinkSaver

Inside it, create two files:

File: manifest.json
json
Copy
Edit
{
  "manifest_version": 3,
  "name": "YouTube Link Saver",
  "version": "1.0",
  "permissions": [
    "contextMenus",
    "scripting",
    "clipboardWrite",
    "activeTab"
  ],
  "background": {
    "service_worker": "background.js"
  },
  "host_permissions": [
    "https://www.youtube.com/watch*",
    "https://www.youtube.com/shorts/*"
  ],
  "action": {
    "default_title": "Save YouTube Link"
  }
}
File: background.js
javascript
Copy
Edit
chrome.contextMenus.create({
  id: "sendYouTubeURL",
  title: "Send to yt-dlp",
  contexts: ["page"],
  documentUrlPatterns: [
    "*://www.youtube.com/watch*",
    "*://www.youtube.com/shorts*"
  ]
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "sendYouTubeURL") {
    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => window.location.href
    }, (results) => {
      const url = results[0].result;
      fetch("http://127.0.0.1:5000/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
      });
    });
  }
});
✅ Step 7: Load the Extension
Open your browser (like Chrome or Opera GX)

Go to: chrome://extensions/

Turn on Developer Mode (top right)

Click Load unpacked

Choose the YouTubeLinkSaver folder you made

✅ How to Use It
Make sure your Python script is running

Open a YouTube video

Right-click anywhere on the page

Click Send to yt-dlp

The link is saved to ytlink.txt in your Documents folder

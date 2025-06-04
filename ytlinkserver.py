from flask import Flask, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/save', methods=['POST'])
def save_url():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return "Missing URL", 400

    docs = os.path.join(os.path.expanduser("~"), "Documents")
    ytlink_path = os.path.join(docs, "ytlink.txt")
    queue_limit = 50

    # Check duplicates in ytlink.txt
    if os.path.exists(ytlink_path):
        with open(ytlink_path, "r", encoding="utf-8") as f:
            if f.read().strip() == url:
                return "Duplicate: already in ytlink.txt", 200

    # Check duplicates in queue files
    for i in range(1, queue_limit + 1):
        qfile = os.path.join(docs, f"Queue{i}.txt")
        if os.path.exists(qfile):
            with open(qfile, "r", encoding="utf-8") as f:
                if f.read().strip() == url:
                    return f"Duplicate: already in Queue{i}.txt", 200

    # Write to ytlink.txt if missing or empty
    if not os.path.exists(ytlink_path) or os.stat(ytlink_path).st_size == 0:
        with open(ytlink_path, "w", encoding="utf-8") as f:
            f.write(url)
        return "Written to ytlink.txt", 200

    # Otherwise, write to first free queue file
    for i in range(1, queue_limit + 1):
        qfile = os.path.join(docs, f"Queue{i}.txt")
        if not os.path.exists(qfile):
            with open(qfile, "w", encoding="utf-8") as f:
                f.write(url)
            return f"Queued to Queue{i}.txt", 200

    return "Queue full", 429

if __name__ == "__main__":
    app.run()

import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load config
config_path = os.path.join(os.path.dirname(__file__), "config.json")
with open(config_path, "r") as f:
    config = json.load(f)

STORAGE = config["storage_path"]
os.makedirs(STORAGE, exist_ok=True)

MAX_QUEUE = 50

def next_queue_path():
    # find any yt-link.* file
    yt_base = None
    for f in os.listdir(STORAGE):
        name = os.path.splitext(f)[0]
        if name == "yt-link":
            yt_base = os.path.join(STORAGE, f)
            break

    # if none exists, create yt-link.txt
    if yt_base is None:
        return os.path.join(STORAGE, "yt-link.txt")

    # otherwise queue system continues


    # Collect valid queue numbers
    nums = []
    for f in os.listdir(STORAGE):
        name = os.path.splitext(f)[0]  # remove extension
        if name.startswith("queue"):
            try:
                num = int(name[5:])
                nums.append(num)
            except:
                continue

    # If no queue files exist, start at 1
    if not nums:
        return os.path.join(STORAGE, "queue1.txt")

    # Normal: highest + 1 if below MAX_QUEUE
    next_num = max(nums) + 1
    if next_num <= MAX_QUEUE:
        return os.path.join(STORAGE, f"queue{next_num}.txt")

    # Queue full? check for gaps from highest to lowest
    for i in range(MAX_QUEUE, 0, -1):
        candidate = os.path.join(STORAGE, f"queue{i}.txt")
        if not os.path.exists(candidate):
            return candidate

    # No available slots
    return None


@app.route("/save", methods=["POST"])
def save_link():
    data = request.get_json(silent=True)
    if not data or "url" not in data:
        return jsonify({"error": "missing url"}), 400

    url = data["url"].strip()
    path = next_queue_path()
    if path is None:
        return jsonify({"error": "queue full"}), 400

    with open(path, "w", encoding="utf-8") as f:
        f.write(url)

    return jsonify({"saved": os.path.basename(path)})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)

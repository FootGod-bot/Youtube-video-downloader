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
    queue_limit = 50

    # Check all .txt and _temp.txt for duplicates
    for i in range(queue_limit + 1):
        base = "ytlink" if i == 0 else f"Queue{i}"
        for suffix in ["", "_temp"]:
            path = os.path.join(docs, f"{base}{suffix}.txt")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    if f.read().strip() == url:
                        return f"Duplicate: already in {base}{suffix}.txt", 200

    # Write to first free _temp.txt file
    for i in range(queue_limit + 1):
        base = "ytlink" if i == 0 else f"Queue{i}"
        final_path = os.path.join(docs, f"{base}.txt")
        temp_path = os.path.join(docs, f"{base}_temp.txt")

        if not os.path.exists(final_path) and not os.path.exists(temp_path):
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(url)
            return f"Written to {base}_temp.txt", 200

    return "Queue full", 429

if __name__ == "__main__":
    app.run()

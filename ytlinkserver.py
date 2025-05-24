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

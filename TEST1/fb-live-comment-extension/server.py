from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

CONFIG = {
    "target_url": "https://www.facebook.com/watch/live/?v=xxxx",
    "comment": "請問現在有優惠嗎"
}

@app.route("/config")
def get_config():
    return jsonify(CONFIG)

if __name__ == "__main__":
    app.run(port=5000)

import os

from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/")
def home():
    return (
        "<h1>Python app deployed successfully!</h1>"
        "<p>This page is running on your AWS EC2 instance.</p>"
    )


@app.get("/health")
def health():
    return jsonify(status="healthy")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))

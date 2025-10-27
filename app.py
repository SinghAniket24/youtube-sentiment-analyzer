from flask import Flask, render_template, request
from youtube_sentiments import build_dashboard  # ✅ import the correct function

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    dashboard = None
    error = None
    if request.method == "POST":
        video_url = request.form.get("video_url")
        dashboard, error = build_dashboard(video_url)
    return render_template("index.html", dashboard=dashboard, error=error)

if __name__ == "__main__":
    try:
        # Try to start on port 5001
        app.run(debug=True, port=5002)
    except OSError:
        # If port 5001 is busy, fallback automatically
        print("⚠️ Port 5001 busy — retrying on port 5002...")
        app.run(debug=True, port=5002)

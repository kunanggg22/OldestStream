from flask import Flask, request, Response
import yt_dlp
import requests
import os

app = Flask(__name__)

@app.route("/stream")
def stream():
    video_id = request.args.get("id")
    if not video_id:
        return {"error": "Missing id"}, 400

    url = f"https://www.youtube.com/watch?v={video_id}"

    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "nocheckcertificate": True,
        "http_headers": {
            "User-Agent": "Mozilla/5.0"
        },
        "js_runtimes": ["node"],
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web", "tv_embedded"]
            }
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info.get("url")

        if not audio_url:
            return {"error": "No audio found"}, 500

        r = requests.get(
            audio_url,
            stream=True,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Range": request.headers.get("Range", "")
            }
        )

        return Response(
            r.iter_content(chunk_size=1024),
            status=r.status_code,
            content_type=r.headers.get("content-type"),
            headers={
                "Accept-Ranges": "bytes",
                "Content-Range": r.headers.get("Content-Range", "")
            }
        )

    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 7860)))

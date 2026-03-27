from flask import Flask, request, jsonify, redirect
import yt_dlp
import os
import tempfile

app = Flask(__name__)

def build_opts(client):
    opts = {
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'skip_download': True,

        # 🔥 pakai bestaudio (biar yt-dlp yang pilih)
        'format': 'bestaudio/best',

        # 🔥 fallback client
        'extractor_args': {
            'youtube': {
                'player_client': [client],
            }
        },

        'nocheckcertificate': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0'
        }
    }

    cookies = os.environ.get('COOKIES_TXT')
    if cookies:
        tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        tmp.write(cookies)
        tmp.flush()
        opts['cookiefile'] = tmp.name

    return opts


@app.route('/')
def index():
    return jsonify({'status': 'ok'})


@app.route('/stream')
def stream():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({'error': 'Missing id'}), 400

    url = f'https://www.youtube.com/watch?v={video_id}'

    # 🔥 urutan fallback (yang paling sering tembus dulu)
    clients = ['android', 'tv_embedded', 'web']

    for client in clients:
        try:
            with yt_dlp.YoutubeDL(build_opts(client)) as ydl:
                info = ydl.extract_info(url, download=False)

                audio_url = info.get('url')
                if audio_url:
                    # 🔥 redirect langsung (lebih ringan & stabil)
                    return redirect(audio_url)

        except Exception as e:
            print(f"[{client}] failed: {e}")
            continue

    return jsonify({'error': 'All clients failed'}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 7860))
    app.run(host='0.0.0.0', port=port)

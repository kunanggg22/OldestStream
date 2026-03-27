from flask import Flask, jsonify, request
import yt_dlp
import os

app = Flask(__name__)

@app.route('/stream')
def stream():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({'error': 'missing id'}), 400

    cookies_path = os.path.join(os.path.dirname(__file__), 'cookies.txt')

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': False,
        'no_warnings': False,
        'cookiefile': cookies_path,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                f'https://www.youtube.com/watch?v={video_id}',
                download=False
            )
            url = info['url']
            return jsonify({'url': url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

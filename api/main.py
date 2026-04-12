from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp
import os
import static_ffmpeg
import traceback

# Initialize FFmpeg (Vercel needs HOME set to /tmp to download binaries)
if os.environ.get('VERCEL'):
    os.environ['HOME'] = '/tmp'

try:
    static_ffmpeg.add_paths()
except Exception as e:
    print(f"FFmpeg init error: {e}")

app = Flask(__name__)
CORS(app)

# Use /tmp for downloads in serverless environments like Vercel
DOWNLOAD_DIR = '/tmp' if os.environ.get('VERCEL') else os.path.join(os.getcwd(), 'downloads')
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/info', methods=['GET', 'POST'])
def get_video_info():
    # Handle both POST (JSON) and GET (query params) for flexibility
    if request.method == 'POST':
        data = request.json or {}
        url = data.get('url')
    else:
        url = request.args.get('url')
    
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'quiet': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration'),
                'uploader': info.get('uploader'),
                'url': url
            })
    except Exception as e:
        print(f"Info error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/download')
def download_video():
    url = request.args.get('url')
    if not url:
        return "URL is required", 400
    
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
        'noplaylist': True,
        'ffmpeg_location': '/tmp' if os.environ.get('VERCEL') else None
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = f"{info['id']}.mp4"
            filepath = os.path.join(DOWNLOAD_DIR, filename)
            
            # Send file and the OS will handle cleanup eventually in serverless
            return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)
    except Exception as e:
        print(f"Download error: {traceback.format_exc()}")
        return str(e), 500

# For local development
if __name__ == '__main__':
    app.run(debug=True, port=5000)

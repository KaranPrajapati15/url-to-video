from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import yt_dlp
import os
import static_ffmpeg
import traceback

# Initialize FFmpeg
try:
    static_ffmpeg.add_paths()
except Exception as e:
    print(f"FFmpeg init error: {e}")

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Use /tmp for downloads (works on Render and most PaaS)
DOWNLOAD_DIR = '/tmp' if os.name != 'nt' else os.path.join(os.getcwd(), 'downloads')
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/info', methods=['GET', 'POST'])
def get_video_info():
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
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = f"{info['id']}.mp4"
            filepath = os.path.join(DOWNLOAD_DIR, filename)
            
            return send_file(filepath, as_attachment=True)
    except Exception as e:
        print(f"Download error: {traceback.format_exc()}")
        return str(e), 500

if __name__ == '__main__':
    # Render uses the PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

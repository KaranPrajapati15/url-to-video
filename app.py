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


def get_base_ydl_opts():
    """Build base yt-dlp options with all anti-bot-detection measures."""
    opts = {
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'source_address': '0.0.0.0',  # Force IPv4
        'socket_timeout': 30,
        'retries': 3,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        },
        'sleep_interval': 1,        # Wait 1s between requests to avoid rate limits
        'max_sleep_interval': 5,
    }

    # Use cookies.txt if it exists to bypass YouTube bot detection
    cookies_path = os.path.join(os.getcwd(), 'cookies.txt')
    if os.path.exists(cookies_path):
        opts['cookiefile'] = cookies_path
        print("[yt-dlp] Using cookies.txt for authentication")

    # Support PO Token via environment variable (for YouTube bot detection bypass)
    po_token = os.environ.get('YT_PO_TOKEN')
    visitor_data = os.environ.get('YT_VISITOR_DATA')

    if po_token and visitor_data:
        opts['extractor_args'] = {
            'youtube': [
                f'player_skip=webpage,configs',
                f'po_token=web+{po_token}',
                f'visitor_data={visitor_data}',
            ]
        }
        print("[yt-dlp] Using PO Token + Visitor Data for authentication")
    # NOTE: We intentionally do NOT set player_client anymore.
    # Modern yt-dlp (2026+) automatically selects the best client.
    # Forcing player_client=android is outdated and causes failures.

    return opts


def try_extract(url, download=False, format_spec='best'):
    """Try extracting video info/download with automatic fallback strategies."""
    base_opts = get_base_ydl_opts()
    base_opts['format'] = format_spec

    if download:
        base_opts['merge_output_format'] = 'mp4'
        base_opts['outtmpl'] = os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s')

    # Strategy list: try default first, then with specific clients as fallback
    strategies = [
        {'name': 'default', 'extra_opts': {}},
        {'name': 'mweb client', 'extra_opts': {
            'extractor_args': {'youtube': ['player_client=mweb']}
        }},
        {'name': 'web_creator client', 'extra_opts': {
            'extractor_args': {'youtube': ['player_client=web_creator']}
        }},
    ]

    # If PO token is configured, only use default (it already has the token)
    if os.environ.get('YT_PO_TOKEN'):
        strategies = [strategies[0]]

    last_error = None
    for strategy in strategies:
        try:
            opts = {**base_opts, **strategy['extra_opts']}
            print(f"[yt-dlp] Trying strategy: {strategy['name']}")
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=download)
                print(f"[yt-dlp] Success with strategy: {strategy['name']}")
                return info
        except Exception as e:
            last_error = e
            error_str = str(e)
            print(f"[yt-dlp] Strategy '{strategy['name']}' failed: {error_str}")
            # If it's not a bot detection error, don't bother trying other strategies
            if 'Sign in to confirm' not in error_str and 'bot' not in error_str.lower():
                break

    raise last_error


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

    try:
        info = try_extract(url, download=False)
        return jsonify({
            'title': info.get('title'),
            'thumbnail': info.get('thumbnail'),
            'duration': info.get('duration'),
            'uploader': info.get('uploader'),
            'url': url
        })
    except Exception as e:
        error_msg = str(e)
        print(f"Info error: {error_msg}")

        # Provide a user-friendly error instead of raw yt-dlp output
        if 'Sign in to confirm' in error_msg or 'bot' in error_msg.lower():
            friendly_error = (
                "YouTube is blocking this request (bot detection). "
                "The server needs a cookies.txt file or PO Token to authenticate. "
                "Please contact the site administrator."
            )
        elif 'Video unavailable' in error_msg:
            friendly_error = "This video is unavailable. It may be private, deleted, or region-locked."
        elif 'Unsupported URL' in error_msg:
            friendly_error = "This URL is not supported. Please check the URL and try again."
        else:
            friendly_error = f"Failed to fetch video info: {error_msg}"

        return jsonify({"error": friendly_error}), 500


@app.route('/download')
def download_video():
    url = request.args.get('url')
    if not url:
        return "URL is required", 400

    try:
        info = try_extract(url, download=True, format_spec='bestvideo+bestaudio/best')
        filename = f"{info['id']}.mp4"
        filepath = os.path.join(DOWNLOAD_DIR, filename)

        return send_file(filepath, as_attachment=True)
    except Exception as e:
        error_msg = str(e)
        print(f"Download error: {traceback.format_exc()}")

        if 'Sign in to confirm' in error_msg or 'bot' in error_msg.lower():
            return "YouTube bot detection triggered. Server needs cookies.txt or PO Token.", 503
        return f"Download failed: {error_msg}", 500


@app.route('/upload-cookies', methods=['POST'])
def upload_cookies():
    """Upload a cookies.txt file to the server for YouTube authentication."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    cookies_path = os.path.join(os.getcwd(), 'cookies.txt')
    file.save(cookies_path)

    return jsonify({"message": "Cookies uploaded successfully. YouTube authentication enabled."})


@app.route('/health')
def health():
    """Health check endpoint with diagnostic info."""
    cookies_exist = os.path.exists(os.path.join(os.getcwd(), 'cookies.txt'))
    po_token_set = bool(os.environ.get('YT_PO_TOKEN'))

    return jsonify({
        'status': 'ok',
        'yt_dlp_version': yt_dlp.version.__version__,
        'cookies_configured': cookies_exist,
        'po_token_configured': po_token_set,
        'auth_method': 'po_token' if po_token_set else ('cookies' if cookies_exist else 'none'),
    })


if __name__ == '__main__':
    # Render uses the PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

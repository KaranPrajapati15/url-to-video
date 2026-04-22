# G-Downloader | Premium Video Downloader

A professional-grade video downloader built with Flask and yt-dlp, optimized for Render.

## Features
- **Multi-platform support**: YouTube, Instagram, TikTok, Twitter, Facebook, etc.
- **Max Quality**: Extracts the best available formats for every video.
- **Premium UI**: Modern, responsive dark theme with glassmorphism and neon accents.

## Deployment to Render

1. Create a new **Web Service** on Render.
2. Connect your GitHub repository.
3. Render will automatically detect the `render.yaml` file and configure:
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

## ⚠️ Fixing YouTube Bot Detection

YouTube blocks requests from cloud servers (Render, Heroku, etc.) when it can't verify you're not a bot. You have two options:

### Option A: Cookies File (Recommended)
1. Open a **private/incognito** browser window
2. Log into YouTube with a throwaway account
3. Navigate to `https://www.youtube.com/robots.txt`
4. Export cookies using a browser extension (e.g., "Get cookies.txt LOCALLY")
5. Place the exported `cookies.txt` file in the project root
6. Commit and redeploy

### Option B: PO Token (Advanced)
Set these environment variables on Render:
- `YT_PO_TOKEN` — your PO token value
- `YT_VISITOR_DATA` — your visitor data value

See the [yt-dlp PO Token Guide](https://github.com/yt-dlp/yt-dlp/wiki/PO-Token-Guide) for details.

## Local Development

### 1. Requirements
Ensure you have Python 3.8+ installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the App
```bash
python app.py
```
The application will run on `http://localhost:5000`. You can access both the frontend and the API from this single URL.

## Tech Stack
- **Backend**: Flask (Python), yt-dlp
- **Frontend**: HTML5, Vanilla CSS3 (Modern UI), JavaScript (ES6+)
- **Deployment**: Render (Web Service)

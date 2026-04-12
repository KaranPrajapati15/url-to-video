# G-Downloader | Premium Video Downloader

A professional-grade video downloader built with Flask and yt-dlp.

## Features
- **Multi-platform support**: YouTube, Instagram, TikTok, Twitter, Facebook, etc.
- **Max Quality**: Extracts the best available formats for every video.
- **Premium UI**: Modern, responsive dark theme with glassmorphism and neon accents.

## How to Run

### 1. Requirements
Ensure you have Python 3.8+ installed. You also need `ffmpeg` installed on your system if you want to merge best video + best audio (though the web app provides direct links to combined formats where available).

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the Backend
```bash
python app.py
```
The backend will run on `http://localhost:5000`.

### 4. Open the Frontend
Simply open `index.html` in your browser or run a simple server:
```bash
python -m http.server 8000
```
Then visit `http://localhost:8000`.

## Tech Stack
- **Backend**: Flask (Python), yt-dlp
- **Frontend**: HTML5, Vanilla CSS3 (Modern UI), JavaScript (ES6+)

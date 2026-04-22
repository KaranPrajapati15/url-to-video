FROM python:3.10-slim

# Install system dependencies: Node.js 20, ffmpeg, git
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    ffmpeg \
    git \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Clone and build the BgUtil PO Token HTTP server (for YouTube bot detection bypass)
RUN git clone --single-branch --branch 1.3.1 \
    https://github.com/Brainicism/bgutil-ytdlp-pot-provider.git /opt/bgutil \
    && cd /opt/bgutil/server \
    && npm ci \
    && npx tsc

# Copy application code
COPY . .

# Create downloads directory
RUN mkdir -p /tmp/downloads

# Expose the Flask port
EXPOSE 5000

# Start script: launch PO token server in background, then start Flask via gunicorn
COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]

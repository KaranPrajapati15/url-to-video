#!/bin/bash
set -e

echo "[STARTUP] Starting BgUtil PO Token HTTP Server on port 4416..."
cd /opt/bgutil/server
node build/main.js &
POT_PID=$!

# Wait for the PO token server to be ready
sleep 3
echo "[STARTUP] PO Token server started (PID: $POT_PID)"

echo "[STARTUP] Starting Flask app via Gunicorn..."
cd /app
PORT=${PORT:-5000}
exec gunicorn app:app --bind 0.0.0.0:$PORT --timeout 300 --workers 2

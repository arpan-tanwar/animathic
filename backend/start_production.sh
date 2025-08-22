#!/bin/bash

# Production startup script for Animathic Backend

set -e

echo "🚀 Starting Animathic Backend in Production Mode..."

# Load environment variables
if [ -f .env ]; then
    echo "📋 Loading environment variables from .env"
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set production environment
export ENVIRONMENT=production
export LOG_LEVEL=INFO

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p /tmp/animathic
mkdir -p /var/log/animathic 2>/dev/null || true

# Activate virtual environment
echo "🐍 Activating Python virtual environment..."
source venv/bin/activate

# Install/upgrade production dependencies
echo "📦 Checking production dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations (if any)
echo "🗄️  Checking database..."
python -c "
from database import init_database
try:
    init_database()
    print('✅ Database initialized successfully')
except Exception as e:
    print(f'⚠️  Database warning: {e}')
    print('Continuing with startup...')
"

# Start the production server
echo "🌐 Starting production server with Gunicorn..."
exec gunicorn main:app \
    --config gunicorn.conf.py \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers ${WORKERS:-4} \
    --bind ${HOST:-0.0.0.0}:${PORT:-8080} \
    --timeout 300 \
    --keepalive 2 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --preload \
    --access-logfile - \
    --error-logfile - \
    --log-level ${LOG_LEVEL:-info}

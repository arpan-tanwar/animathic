#!/bin/bash

# Production Deployment Script for Animathic Backend

set -e

echo "🚀 Deploying Animathic Backend to Production..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root (for production deployment)
if [[ $EUID -eq 0 ]]; then
   echo -e "${YELLOW}⚠️  Running as root - this is fine for production deployment${NC}"
else
   echo -e "${YELLOW}ℹ️  Running as non-root user - some operations may require sudo${NC}"
fi

# Create production directories
echo "📁 Creating production directories..."
sudo mkdir -p /var/log/animathic
sudo mkdir -p /tmp/animathic
sudo chown -R $USER:$USER /var/log/animathic /tmp/animathic 2>/dev/null || true

# Stop existing services
echo "🛑 Stopping existing services..."
sudo pkill -f "python main.py" 2>/dev/null || true
sudo pkill -f "gunicorn" 2>/dev/null || true
sudo lsof -ti:8080 | xargs sudo kill -9 2>/dev/null || true

# Wait for processes to stop
sleep 2

# Activate virtual environment
echo "🐍 Activating Python virtual environment..."
source venv/bin/activate

# Install/upgrade production dependencies
echo "📦 Installing production dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install gunicorn if not present
if ! pip show gunicorn > /dev/null 2>&1; then
    echo "📦 Installing Gunicorn..."
    pip install gunicorn
fi

# Set production environment variables
export ENVIRONMENT=production
export LOG_LEVEL=INFO
export HOST=0.0.0.0
export PORT=8080
export WORKERS=4

# Test database connection
echo "🗄️  Testing database connection..."
python -c "
from database import init_database
try:
    init_database()
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

# Test basic functionality
echo "🧪 Testing basic functionality..."
python -c "
from services.manim_api_docs import ManimAPIDocumentationSystem
from services.enhanced_manim_generator import EnhancedManimCodeGenerator
from services.clerk_auth import ClerkAuthService
from services.supabase_storage import SupabaseStorageService

try:
    # Test enhanced workflow components
    manim_docs = ManimAPIDocumentationSystem()
    code_generator = EnhancedManimCodeGenerator(manim_docs)
    
    # Test old services for compatibility
    clerk_service = ClerkAuthService()
    storage_service = SupabaseStorageService()
    
    print('✅ All services initialized successfully')
    print(f'✅ Enhanced workflow: {len(manim_docs.symbol_registry)} Manim symbols available')
except Exception as e:
    print(f'❌ Service initialization failed: {e}')
    exit(1)
"

# Start production server
echo "🌐 Starting production server..."
nohup gunicorn main:app \
    --config gunicorn.conf.py \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers ${WORKERS} \
    --bind ${HOST}:${PORT} \
    --timeout 300 \
    --keepalive 2 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --preload \
    --access-logfile /var/log/animathic/access.log \
    --error-logfile /var/log/animathic/error.log \
    --log-level ${LOG_LEVEL} \
    > /var/log/animathic/startup.log 2>&1 &

# Get the process ID
SERVER_PID=$!
echo "📝 Server started with PID: $SERVER_PID"

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 5

# Test server health
echo "🏥 Testing server health..."
for i in {1..10}; do
    if curl -s http://localhost:${PORT}/api/health > /dev/null; then
        echo -e "${GREEN}✅ Server is healthy and responding!${NC}"
        break
    else
        echo "⏳ Attempt $i/10: Server not ready yet..."
        sleep 2
    fi
    
    if [ $i -eq 10 ]; then
        echo -e "${RED}❌ Server failed to start after 10 attempts${NC}"
        echo "📋 Checking logs..."
        tail -20 /var/log/animathic/startup.log
        exit 1
    fi
done

# Save PID to file for management
echo $SERVER_PID > /var/run/animathic-backend.pid

# Show server status
echo "📊 Server Status:"
echo "   PID: $SERVER_PID"
echo "   Port: ${PORT}"
echo "   Workers: ${WORKERS}"
echo "   Logs: /var/log/animathic/"
echo "   Health: http://localhost:${PORT}/api/health"

# Test a simple API call
echo "🧪 Testing API endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:${PORT}/api/health)
echo "   Health Response: $HEALTH_RESPONSE"

echo -e "${GREEN}🎉 Production deployment completed successfully!${NC}"
echo ""
echo "📋 Next steps:"
echo "   1. Test the frontend integration"
echo "   2. Monitor logs: tail -f /var/log/animathic/error.log"
echo "   3. Check server status: ps aux | grep gunicorn"
echo "   4. Stop server: sudo kill \$(cat /var/run/animathic-backend.pid)"

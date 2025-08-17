# 🚀 Quick Start Guide - Optimized Animathic Backend

## ✅ Error Fixed!

The `psutil` dependency has been installed and all optimizations are working correctly.

## 🏃‍♂️ Quick Start

### Option 1: Auto-Setup (Recommended)

```bash
cd backend
python start_optimized.py
```

This script will:

- Check for required environment variables
- Guide you through setup if anything is missing
- Start the optimized server automatically

### Option 2: Manual Setup

```bash
cd backend

# 1. Set environment variables
export GOOGLE_API_KEY=your_google_api_key_here

# 2. Run the optimized server
python main_optimized.py
```

### Option 3: Development with .env file

```bash
cd backend

# 1. Create .env file
echo "GOOGLE_API_KEY=your_key_here" > .env

# 2. Start server
python start_optimized.py
```

## 🧪 Testing

Test all optimizations without API keys:

```bash
python test_optimized.py
```

## 🛠️ Utilities

### Clean up old media files

```bash
# Dry run (see what would be deleted)
python cleanup_media.py --dry-run --verbose

# Actually clean up files older than 24 hours
python cleanup_media.py --max-age-hours 24
```

### Monitor performance

```bash
# Check health
curl http://localhost:8000/api/health

# Get detailed metrics
curl http://localhost:8000/api/metrics
```

## 📊 Optimized Features

✅ **Security**: Input validation, code injection prevention, rate limiting  
✅ **Performance**: Memory monitoring, resource limits, process isolation  
✅ **Reliability**: Enhanced error handling, automatic cleanup, comprehensive logging  
✅ **AI Quality**: Improved prompts, better validation, higher success rate

## 🔧 Configuration

The optimized backend uses environment-based configuration:

- **Development**: `ENVIRONMENT=development` (default)
- **Staging**: `ENVIRONMENT=staging`
- **Production**: `ENVIRONMENT=production`

Each environment has optimized settings for security and performance.

## 📚 API Documentation

Once running, access documentation at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/health

## ⚠️ Troubleshooting

**Missing GOOGLE_API_KEY**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

**Import errors**: Make sure you're in the backend directory and have installed dependencies:

```bash
pip install -r requirements_optimized.txt
```

**Permission errors**: Make sure scripts are executable:

```bash
chmod +x *.py
```

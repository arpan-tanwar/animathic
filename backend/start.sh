#!/bin/bash

echo "Starting Animathic Backend..."
echo "PORT: $PORT"
echo "Current directory: $(pwd)"
echo "Files in current directory:"
ls -la

echo "Testing Python script execution..."
python3 -c "
import sys
print('Python version:', sys.version)
print('Python path:', sys.path)
print('Testing basic Python execution...')
print('All good!')
"

echo "Testing Python imports step by step..."
python3 -c "
print('1. Testing basic imports...')
import os
import sys
import logging
print('✓ Basic imports successful')

print('2. Testing dotenv...')
from dotenv import load_dotenv
load_dotenv()
print('✓ dotenv successful')

print('3. Testing FastAPI...')
from fastapi import FastAPI
print('✓ FastAPI import successful')

print('4. Testing SQLAlchemy...')
from sqlalchemy import create_engine
print('✓ SQLAlchemy import successful')

print('5. Testing database module...')
try:
    from database import engine, SessionLocal
    print('✓ Database module import successful')
    if engine:
        print('✓ Database engine available')
    else:
        print('⚠ Database engine not available')
except Exception as e:
    print(f'✗ Database module import failed: {e}')

print('6. Testing models...')
try:
    from models.database import User, Video, GenerationJob, Feedback
    print('✓ Models import successful')
except Exception as e:
    print(f'✗ Models import failed: {e}')

print('7. Testing services...')
try:
    from services.ai_service_new import AIService
    print('✓ AI Service import successful')
except Exception as e:
    print(f'✗ AI Service import failed: {e}')

print('8. Testing production config...')
try:
    from production_config import ALLOWED_ORIGINS, DEBUG
    print('✓ Production config import successful')
except Exception as e:
    print(f'✗ Production config import failed: {e}')

print('All imports tested!')
"

echo "Testing main.py import..."
python3 -c "
try:
    import main
    print('✓ main.py import successful')
    print(f'✓ FastAPI app created: {main.app}')
    print(f'✓ App title: {main.app.title}')
except Exception as e:
    print(f'✗ main.py import failed: {e}')
    import traceback
    traceback.print_exc()
"

echo "Starting Uvicorn with FastAPI app..."
echo "Command: uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080} --log-level info"

# Try to start Uvicorn with the FastAPI app
exec uvicorn main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8080} \
    --log-level info

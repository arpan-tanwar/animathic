# Animathic Backend Setup Guide

## Required Environment Variables

The backend requires the following environment variables to be set:

### Essential Variables

1. **GOOGLE_AI_API_KEY**

   - Required for AI animation generation using Gemini 2.5 Flash
   - Get this from [Google AI Studio](https://aistudio.google.com/)
   - Example: `GOOGLE_AI_API_KEY=AIzaSyC...`

2. **DATABASE_URL**
   - Required for database operations
   - Should point to a Supabase Postgres instance
   - Format: `postgresql://username:password@host:port/database?sslmode=require`
   - Example: `DATABASE_URL=postgresql://postgres:password@db.supabase.co:5432/postgres?sslmode=require`

### Optional Variables

3. **SUPABASE_URL**

   - For video storage (if using Supabase)
   - Example: `SUPABASE_URL=https://your-project.supabase.co`

4. **SUPABASE_SERVICE_KEY**

   - For authenticated access to Supabase storage
   - Example: `SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

5. **SUPABASE_NEW_BUCKET** and **SUPABASE_OLD_BUCKET**

   - Bucket names for video storage
   - Defaults: `animathic-media` and `manim-videos`

6. **LOCAL_INFERENCE_URL**
   - Fallback local AI service (optional)
   - Example: `LOCAL_INFERENCE_URL=http://localhost:8000/infer`

## Setup Steps

1. **Install Dependencies**

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**

   ```bash
   export GOOGLE_AI_API_KEY="your_key_here"
   export DATABASE_URL="your_database_url_here"
   ```

3. **Run the Backend**
   ```bash
   python main.py
   ```

## Troubleshooting

### Common Issues

1. **"GOOGLE_AI_API_KEY is not set"**

   - Make sure you've set the environment variable
   - Check that the API key is valid

2. **Database connection errors**

   - Verify DATABASE_URL is correct
   - Ensure the database is accessible
   - Check SSL requirements for Supabase

3. **Manim not found**

   - Install Manim: `pip install manim`
   - Ensure Manim is in your PATH

4. **Video generation fails**
   - Check Manim installation
   - Verify the generated code is valid
   - Check system resources (memory, disk space)

## Development

- The backend uses FastAPI for the web framework
- AI service integrates with Google's Gemini 2.5 Flash
- Manim is used for mathematical animation generation
- Videos are stored in Supabase storage buckets
- Jobs are tracked both in-memory and in the database

## API Endpoints

- `POST /api/generate` - Start animation generation
- `GET /api/status/{job_id}` - Check generation status
- `GET /api/videos` - List user videos
- `GET /api/health` - Health check

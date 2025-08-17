# 🗄️ Database Setup Guide - Enhanced Video Storage System

## 📋 Overview

The enhanced Animathic system now includes comprehensive database integration for tracking users, videos, and generation analytics. This guide will help you set up and deploy the new database-powered system.

## 🚀 New Features

### ✨ **Comprehensive User Management**

- User profiles with statistics
- Video tracking per user
- Generation time analytics
- Storage usage monitoring

### 🎬 **Advanced Video Management**

- Complete video metadata storage
- File size and duration tracking
- Video resolution information
- Status tracking (processing, completed, failed)
- Custom tags and categorization

### 📊 **Analytics & Logging**

- Detailed generation logs with attempt tracking
- AI model performance metrics
- Error tracking and debugging
- User activity monitoring
- Popular prompt analysis

### 🔧 **Enhanced API Endpoints**

- `/api/generate` - Generate videos with database integration
- `/api/videos` - List user videos with filtering
- `/api/videos/{id}` - Get specific video details
- `/api/videos/{id}/tags` - Update video tags
- `/api/analytics` - Comprehensive user analytics
- `/health` - System health monitoring

## 🛠️ Setup Instructions

### 1. **Install New Dependencies**

```bash
cd backend
pip install -r requirements.txt
```

New dependencies added:

- `sqlalchemy>=2.0.0` - ORM for database operations
- `psycopg2-binary>=2.9.0` - PostgreSQL driver
- `alembic>=1.13.0` - Database migrations

### 2. **Database Configuration**

#### Option A: Using Supabase (Recommended)

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Create a new project or use existing
3. Go to Settings → Database
4. Copy the connection string
5. Add to your environment variables:

```bash
DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:5432/[DATABASE]
SUPABASE_URL=https://[PROJECT_ID].supabase.co
SUPABASE_SERVICE_KEY=[YOUR_SERVICE_KEY]
```

#### Option B: Local PostgreSQL

```bash
# Install PostgreSQL
brew install postgresql  # macOS
sudo apt-get install postgresql  # Ubuntu

# Create database
createdb animathic_db

# Set environment variable
DATABASE_URL=postgresql://localhost/animathic_db
```

### 3. **Run Database Migrations**

Execute the SQL migration file in your database:

```sql
-- Connect to your database and run:
\i migrations/002_enhanced_video_storage.sql
```

Or via Supabase dashboard:

1. Go to SQL Editor
2. Copy contents of `migrations/002_enhanced_video_storage.sql`
3. Execute the SQL

### 4. **Update Environment Variables**

Create or update your `.env` file:

```bash
# Database
DATABASE_URL=postgresql://your_connection_string
SUPABASE_URL=https://your_project.supabase.co
SUPABASE_SERVICE_KEY=your_service_key

# AI
GOOGLE_API_KEY=your_gemini_api_key

# Storage
MEDIA_DIR=media
```

### 5. **Switch to Enhanced System**

Replace the current system with the enhanced version:

```bash
# Backup current main.py
mv main.py main_legacy.py

# Use enhanced version
mv main_enhanced.py main.py

# Update service imports if needed
```

### 6. **Test the System**

```bash
# Test structure (no dependencies required)
python test_structure_only.py

# Test with dependencies installed
python test_enhanced_system.py

# Start the server
python main.py
```

## 📊 Database Schema

### **Users Table**

```sql
- id (TEXT, PRIMARY KEY) -- Clerk user ID
- email (TEXT)
- name (TEXT)
- videos_count (INTEGER)
- total_generation_time (FLOAT)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
- last_activity (TIMESTAMP)
- metadata (JSONB)
```

### **Videos Table**

```sql
- id (UUID, PRIMARY KEY)
- user_id (TEXT, FOREIGN KEY)
- title (TEXT)
- prompt (TEXT, NOT NULL)
- file_path (TEXT)
- file_size (BIGINT)
- duration (FLOAT)
- resolution_width (INTEGER)
- resolution_height (INTEGER)
- status (TEXT) -- processing, completed, failed, deleted
- generation_time (FLOAT)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
- metadata (JSONB)
- tags (TEXT[])
```

### **Generation Logs Table**

```sql
- id (UUID, PRIMARY KEY)
- video_id (UUID, FOREIGN KEY)
- user_id (TEXT, FOREIGN KEY)
- prompt (TEXT)
- status (TEXT) -- started, code_generated, rendering, completed, failed
- attempt_number (INTEGER)
- error_message (TEXT)
- execution_time (FLOAT)
- ai_model (TEXT)
- generated_code (TEXT)
- created_at (TIMESTAMP)
- metadata (JSONB)
```

## 🔍 Key Improvements

### **Before (Legacy System)**

```javascript
// Simple storage without tracking
{
  "video_url": "https://storage.url/video.mp4",
  "metadata": {
    "prompt": "user prompt",
    "created_at": "timestamp"
  }
}
```

### **After (Enhanced System)**

```javascript
{
  "video_id": "uuid",
  "video_url": "https://storage.url/video.mp4",
  "metadata": {
    "id": "uuid",
    "user_id": "clerk_id",
    "title": "Animation Title",
    "prompt": "user prompt",
    "file_size": 1234567,
    "duration": 12.5,
    "resolution_width": 1280,
    "resolution_height": 720,
    "status": "completed",
    "generation_time": 45.2,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:31:00Z",
    "tags": ["math", "geometry", "animation"]
  }
}
```

## 📈 Analytics Available

### **User Analytics**

- Total videos created
- Generation time statistics
- Storage usage
- Activity patterns
- Success/failure rates

### **System Analytics**

- Popular prompts
- AI model performance
- Error patterns
- Usage trends
- Resource utilization

## 🔧 Migration from Legacy System

### **Automatic Data Migration**

The new system is backward compatible. Existing videos will:

1. Continue to work with current URLs
2. Be gradually migrated to new schema
3. Maintain all existing functionality

### **Gradual Rollout**

1. Deploy enhanced system alongside legacy
2. Route new requests to enhanced system
3. Migrate existing data in background
4. Deprecate legacy endpoints

## 🚨 Troubleshooting

### **Common Issues**

#### Database Connection Errors

```bash
# Check DATABASE_URL format
DATABASE_URL=postgresql://user:password@host:port/database

# Test connection
python -c "from models.database import get_db_manager; get_db_manager()"
```

#### Migration Errors

```bash
# Check if tables exist
psql $DATABASE_URL -c "\dt"

# Manually run migration
psql $DATABASE_URL -f migrations/002_enhanced_video_storage.sql
```

#### Import Errors

```bash
# Install missing dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sqlalchemy; print('SQLAlchemy installed')"
```

## 📞 Support

If you encounter any issues:

1. **Check Logs**: Enhanced logging provides detailed error information
2. **Verify Environment**: Ensure all environment variables are set correctly
3. **Test Database**: Use provided test scripts to validate setup
4. **Review Migration**: Ensure SQL migration completed successfully

## 🎉 Ready for Production!

Once setup is complete, your enhanced Animathic system will provide:

- ✅ **Comprehensive user and video management**
- ✅ **Advanced analytics and monitoring**
- ✅ **Scalable database architecture**
- ✅ **Enhanced debugging and logging**
- ✅ **Future-ready extensibility**

The system is now ready to handle production workloads with professional-grade database integration!

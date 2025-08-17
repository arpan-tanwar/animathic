-- Enhanced video storage schema with improved structure
-- Drop existing table if needed (for migration)
-- DROP TABLE IF EXISTS videos CASCADE;

-- Create enhanced videos table
CREATE TABLE IF NOT EXISTS videos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,  -- Clerk user ID
    title TEXT,
    prompt TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT,
    duration FLOAT,  -- Duration in seconds
    resolution_width INTEGER DEFAULT 1280,
    resolution_height INTEGER DEFAULT 720,
    status TEXT DEFAULT 'processing' CHECK (status IN ('processing', 'completed', 'failed', 'deleted')),
    generation_time FLOAT,  -- Time taken to generate in seconds
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb,
    tags TEXT[] DEFAULT '{}',  -- Array of tags for categorization
    
    -- Add constraints
    CONSTRAINT videos_file_size_positive CHECK (file_size > 0),
    CONSTRAINT videos_duration_positive CHECK (duration > 0),
    CONSTRAINT videos_generation_time_positive CHECK (generation_time > 0)
);

-- Create users table to track user statistics
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,  -- Clerk user ID
    email TEXT,
    name TEXT,
    videos_count INTEGER DEFAULT 0,
    total_generation_time FLOAT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create generation_logs table for analytics and debugging
CREATE TABLE IF NOT EXISTS generation_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    prompt TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('started', 'code_generated', 'rendering', 'completed', 'failed')),
    attempt_number INTEGER DEFAULT 1,
    error_message TEXT,
    execution_time FLOAT,
    ai_model TEXT DEFAULT 'gemini-2.5-flash',
    generated_code TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_videos_user_id ON videos(user_id);
CREATE INDEX IF NOT EXISTS idx_videos_created_at ON videos(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status);
CREATE INDEX IF NOT EXISTS idx_videos_tags ON videos USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_users_last_activity ON users(last_activity DESC);
CREATE INDEX IF NOT EXISTS idx_generation_logs_video_id ON generation_logs(video_id);
CREATE INDEX IF NOT EXISTS idx_generation_logs_user_id ON generation_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_generation_logs_status ON generation_logs(status);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
DROP TRIGGER IF EXISTS update_videos_updated_at ON videos;
CREATE TRIGGER update_videos_updated_at 
    BEFORE UPDATE ON videos 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Function to update user statistics when videos are added/removed
CREATE OR REPLACE FUNCTION update_user_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        -- Insert or update user record
        INSERT INTO users (id, videos_count, total_generation_time, last_activity)
        VALUES (NEW.user_id, 1, COALESCE(NEW.generation_time, 0), CURRENT_TIMESTAMP)
        ON CONFLICT (id) DO UPDATE SET
            videos_count = users.videos_count + 1,
            total_generation_time = users.total_generation_time + COALESCE(NEW.generation_time, 0),
            last_activity = CURRENT_TIMESTAMP;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        -- Update user stats when video is deleted
        UPDATE users SET
            videos_count = GREATEST(videos_count - 1, 0),
            total_generation_time = GREATEST(total_generation_time - COALESCE(OLD.generation_time, 0), 0),
            last_activity = CURRENT_TIMESTAMP
        WHERE id = OLD.user_id;
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        -- Update user stats when video generation time changes
        IF OLD.generation_time IS DISTINCT FROM NEW.generation_time THEN
            UPDATE users SET
                total_generation_time = total_generation_time - COALESCE(OLD.generation_time, 0) + COALESCE(NEW.generation_time, 0),
                last_activity = CURRENT_TIMESTAMP
            WHERE id = NEW.user_id;
        END IF;
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

-- Create trigger for user statistics
DROP TRIGGER IF EXISTS update_user_stats_trigger ON videos;
CREATE TRIGGER update_user_stats_trigger
    AFTER INSERT OR UPDATE OR DELETE ON videos
    FOR EACH ROW
    EXECUTE FUNCTION update_user_stats();

-- Enable Row Level Security
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE generation_logs ENABLE ROW LEVEL SECURITY;

-- Create policies for videos table
DROP POLICY IF EXISTS "Users can only access their own videos" ON videos;
CREATE POLICY "Users can only access their own videos"
    ON videos
    FOR ALL
    USING (user_id = current_setting('app.current_user_id', true))
    WITH CHECK (user_id = current_setting('app.current_user_id', true));

-- Create policies for users table
DROP POLICY IF EXISTS "Users can only access their own data" ON users;
CREATE POLICY "Users can only access their own data"
    ON users
    FOR ALL
    USING (id = current_setting('app.current_user_id', true))
    WITH CHECK (id = current_setting('app.current_user_id', true));

-- Create policies for generation_logs table
DROP POLICY IF EXISTS "Users can only access their own logs" ON generation_logs;
CREATE POLICY "Users can only access their own logs"
    ON generation_logs
    FOR ALL
    USING (user_id = current_setting('app.current_user_id', true))
    WITH CHECK (user_id = current_setting('app.current_user_id', true));

-- Create views for analytics
CREATE OR REPLACE VIEW user_analytics AS
SELECT 
    u.id,
    u.email,
    u.name,
    u.videos_count,
    u.total_generation_time,
    u.created_at as user_since,
    u.last_activity,
    COUNT(v.id) as actual_video_count,
    AVG(v.generation_time) as avg_generation_time,
    SUM(v.file_size) as total_storage_used,
    COUNT(CASE WHEN v.status = 'completed' THEN 1 END) as completed_videos,
    COUNT(CASE WHEN v.status = 'failed' THEN 1 END) as failed_videos
FROM users u
LEFT JOIN videos v ON u.id = v.user_id
GROUP BY u.id, u.email, u.name, u.videos_count, u.total_generation_time, u.created_at, u.last_activity;

-- Create view for popular prompts
CREATE OR REPLACE VIEW popular_prompts AS
SELECT 
    prompt,
    COUNT(*) as usage_count,
    AVG(generation_time) as avg_generation_time,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as success_count,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failure_count,
    MAX(created_at) as last_used
FROM videos
WHERE prompt IS NOT NULL
GROUP BY prompt
ORDER BY usage_count DESC, last_used DESC;

-- Insert some sample data for testing (optional)
-- INSERT INTO users (id, email, name) VALUES 
--     ('test_user_1', 'test1@example.com', 'Test User 1'),
--     ('test_user_2', 'test2@example.com', 'Test User 2')
-- ON CONFLICT (id) DO NOTHING;

-- Add comments for documentation
COMMENT ON TABLE videos IS 'Stores video metadata and file information';
COMMENT ON TABLE users IS 'User statistics and profile information';
COMMENT ON TABLE generation_logs IS 'Detailed logs of video generation process for analytics';
COMMENT ON VIEW user_analytics IS 'Comprehensive user statistics and analytics';
COMMENT ON VIEW popular_prompts IS 'Analytics on prompt usage and success rates';

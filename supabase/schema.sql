-- Enable the uuid-ossp extension if not already enabled (useful for uuid_generate_v4)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create the news_articles table
CREATE TABLE news_articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    original_url TEXT NOT NULL UNIQUE,
    source_name TEXT NOT NULL,
    ai_summary TEXT,
    ai_keywords TEXT[],
    category TEXT,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security (RLS)
ALTER TABLE news_articles ENABLE ROW LEVEL SECURITY;

-- 1. Read Access for Public
-- Allows anyone (including anonymous users) to read the news articles.
CREATE POLICY "Allow public read access" 
ON news_articles 
FOR SELECT 
USING (true);

-- 2. Strict Write Access
-- By enabling RLS, all actions (insert/update/delete) are denied by default for `anon` and `authenticated` roles.
-- The Supabase `service_role` key automatically bypasses RLS, so it will have full write access.
-- Therefore, we do not need to grant explicit write access policies for the service role, 
-- and keeping no insert/update/delete policies effectively locks down writes for everyone else!

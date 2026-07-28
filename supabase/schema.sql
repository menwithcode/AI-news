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

-- No policies: deny-all for `anon`/`authenticated` via Supabase's Data API
-- (PostgREST), which this project never uses -- both the frontend and the
-- ingestion script connect directly as the table owner via DATABASE_URL,
-- which bypasses RLS entirely regardless of policies.
--
-- Migration (2026-07-28, security review): originally had an explicit
-- "Allow public read access" policy here, from when the plan was to read
-- via supabase-js + anon key. That path was dropped early on in favor of
-- direct Postgres access, but the permissive policy was left in place --
-- meaning anyone with the anon key could read this table over the Data
-- API, completely bypassing the app's login gate. Removed; see
-- DROP POLICY below for the exact fix applied to the live DB.
DROP POLICY IF EXISTS "Allow public read access" ON news_articles;

-- Migration (2026-07-28): popularity metric, meaning depends on category
-- (GitHub stars, Hugging Face likes, arXiv citation count). NULL where no
-- metric applies (News, Review).
ALTER TABLE news_articles ADD COLUMN IF NOT EXISTS popularity_score INTEGER;

-- Migration (2026-07-28): Web Push subscriptions, one row per subscribed
-- browser/device.
CREATE TABLE IF NOT EXISTS push_subscriptions (
    endpoint TEXT PRIMARY KEY,
    p256dh TEXT NOT NULL,
    auth TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Migration (2026-07-28, security review): enable RLS with no policies
-- (deny-all via the Data API) -- same reasoning as news_articles above.
ALTER TABLE push_subscriptions ENABLE ROW LEVEL SECURITY;

-- Migration (2026-07-28, security review): track failed login attempts
-- per IP for basic brute-force rate limiting on /api/login.
CREATE TABLE IF NOT EXISTS login_attempts (
    id SERIAL PRIMARY KEY,
    ip TEXT NOT NULL,
    attempted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_login_attempts_ip_time ON login_attempts (ip, attempted_at);
ALTER TABLE login_attempts ENABLE ROW LEVEL SECURITY;

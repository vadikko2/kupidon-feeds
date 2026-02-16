-- Feeds service initial schema
-- Apply with: psql -f 001_initial_schema.sql (or \i 001_initial_schema.sql after \c your_database)
\c feeds;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Feeds (no computed fields; likes_count, views_count, has_followed, has_liked are computed at read time)
CREATE TABLE IF NOT EXISTS feeds (
    feed_id UUID PRIMARY KEY,
    account_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    text TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_feeds_account_id ON feeds (account_id);
CREATE INDEX IF NOT EXISTS ix_feeds_created_at ON feeds (created_at);

-- 2. Followers
CREATE TABLE IF NOT EXISTS followers (
    follower VARCHAR(255) NOT NULL,
    follow_for VARCHAR(255) NOT NULL,
    followed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (follower, follow_for)
);

CREATE INDEX IF NOT EXISTS idx_followers_follower ON followers (follower);
CREATE INDEX IF NOT EXISTS idx_followers_follow_for ON followers (follow_for);
CREATE INDEX IF NOT EXISTS idx_followers_composite ON followers (follower, follow_for);

-- 3. Images
CREATE TABLE IF NOT EXISTS images (
    image_id UUID PRIMARY KEY,
    feed_id UUID REFERENCES feeds(feed_id) ON DELETE SET NULL,
    uploader VARCHAR(255) NOT NULL,
    url VARCHAR(2048) NOT NULL,
    blurhash VARCHAR(255),
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "order" INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS ix_images_feed_id ON images (feed_id);
CREATE INDEX IF NOT EXISTS ix_images_uploader ON images (uploader);
CREATE INDEX IF NOT EXISTS ix_images_uploaded_at ON images (uploaded_at);

-- 4. Likes
CREATE TABLE IF NOT EXISTS likes (
    feed_id UUID NOT NULL REFERENCES feeds(feed_id) ON DELETE CASCADE,
    account_id VARCHAR(255) NOT NULL,
    liked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (feed_id, account_id)
);

CREATE INDEX IF NOT EXISTS idx_likes_feed_account ON likes (feed_id, account_id);
CREATE INDEX IF NOT EXISTS ix_likes_feed_id ON likes (feed_id);
CREATE INDEX IF NOT EXISTS ix_likes_account_id ON likes (account_id);
CREATE INDEX IF NOT EXISTS ix_likes_liked_at ON likes (liked_at);

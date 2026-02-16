-- Performance: remove redundant indexes (duplicate PK), add composite indexes for hot paths.
-- Hot path: get_account_feeds (account_id + ORDER BY created_at DESC).
\c feeds;
-- Redundant: PK (feed_id, account_id) already creates unique index on likes
DROP INDEX IF EXISTS idx_likes_feed_account;

-- Redundant: PK (feed_id, account_id) already creates unique index on views
DROP INDEX IF EXISTS idx_views_feed_account;

-- Redundant: PK (follower, follow_for) already creates unique index on followers
DROP INDEX IF EXISTS idx_followers_composite;

-- Hot path: feeds by account_id ordered by created_at DESC (get_account_feeds, get_by_ids follow-up)
CREATE INDEX IF NOT EXISTS ix_feeds_account_created_desc
  ON feeds (account_id, created_at DESC);

-- Likes by feed_id ordered by liked_at DESC (get_by_feed_id pagination)
CREATE INDEX IF NOT EXISTS ix_likes_feed_liked_at_desc
  ON likes (feed_id, liked_at DESC);

-- Followers: who follows account_id, ordered by followed_at DESC
CREATE INDEX IF NOT EXISTS ix_followers_follow_for_followed_at_desc
  ON followers (follow_for, followed_at DESC);

-- Following: who account_id follows, ordered by followed_at DESC
CREATE INDEX IF NOT EXISTS ix_followers_follower_followed_at_desc
  ON followers (follower, followed_at DESC);

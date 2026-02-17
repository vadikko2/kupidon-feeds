-- Performance: index for "my likes" subquery in get_by_ids / get_by_id.
-- Query: WHERE feed_id = ANY($1::uuid[]) AND account_id = $2
\c feeds;

CREATE INDEX IF NOT EXISTS ix_likes_account_feed ON likes (account_id, feed_id);

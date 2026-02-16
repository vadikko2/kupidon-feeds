-- Views table (feed views by account)
\c feeds;

CREATE TABLE IF NOT EXISTS views (
    feed_id UUID NOT NULL REFERENCES feeds(feed_id) ON DELETE CASCADE,
    account_id VARCHAR(255) NOT NULL,
    viewed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (feed_id, account_id)
);

CREATE INDEX IF NOT EXISTS idx_views_feed_account ON views (feed_id, account_id);
CREATE INDEX IF NOT EXISTS ix_views_feed_id ON views (feed_id);
CREATE INDEX IF NOT EXISTS ix_views_account_id ON views (account_id);
CREATE INDEX IF NOT EXISTS ix_views_viewed_at ON views (viewed_at);

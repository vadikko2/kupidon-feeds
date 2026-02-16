import uuid

from domain.entities import feed as feed_entity, images as images_entity
from infrastructure.persistent.postgres.base import BaseRepository
from service import exceptions
from service.interfaces.repositories import feeds as feeds_interface

_FEED_SELECT = """
    SELECT
        f.feed_id,
        f.account_id,
        f.created_at,
        f.updated_at,
        f.text,
        (SELECT count(*)::int FROM likes l WHERE l.feed_id = f.feed_id) AS likes_count,
        (SELECT count(*)::int FROM views v WHERE v.feed_id = f.feed_id) AS views_count,
        (SELECT CASE WHEN $2::text IS NULL THEN false ELSE EXISTS(
            SELECT 1 FROM followers fl
            WHERE fl.follower = $2 AND fl.follow_for = f.account_id
        ) END) AS has_followed,
        (SELECT CASE WHEN $2::text IS NULL THEN false ELSE EXISTS(
            SELECT 1 FROM likes l
            WHERE l.feed_id = f.feed_id AND l.account_id = $2
        ) END) AS has_liked
    FROM feeds f
"""

# Same as _FEED_SELECT but with total_count for pagination (one query for list + total)
_FEED_SELECT_WITH_TOTAL = (
    _FEED_SELECT.strip().removesuffix("FROM feeds f")
    + """,
        count(*) OVER () AS total_count
    FROM feeds f
"""
)


def _row_to_feed(row, images: list[images_entity.Image]) -> feed_entity.Feed:
    has_followed = (
        bool(row["has_followed"]) if row.get("has_followed") is not None else False
    )
    has_liked = bool(row["has_liked"]) if row.get("has_liked") is not None else False
    return feed_entity.Feed(
        feed_id=row["feed_id"],
        account_id=row["account_id"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        text=row["text"],
        images=images,
        likes_count=int(row["likes_count"])
        if row.get("likes_count") is not None
        else 0,
        views_count=int(row["views_count"])
        if row.get("views_count") is not None
        else 0,
        has_followed=has_followed,
        has_liked=has_liked,
    )


def _row_to_image(row) -> images_entity.Image:
    return images_entity.Image(
        image_id=row["image_id"],
        feed_id=row["feed_id"],
        uploader=row["uploader"],
        url=row["url"],
        blurhash=row["blurhash"],
        uploaded_at=row["uploaded_at"],
        order=row["order"],
    )


class PostgresFeedsRepository(BaseRepository, feeds_interface.IFeedsRepository):
    async def exists(self, feed_id: uuid.UUID) -> bool:
        row = await self.conn.fetchrow(
            "SELECT 1 FROM feeds WHERE feed_id = $1",
            feed_id,
        )
        return row is not None

    async def add(self, feed: feed_entity.Feed) -> None:
        if await self.exists(feed.feed_id):
            raise exceptions.FeedAlreadyExists(feed_id=feed.feed_id)
        await self.conn.execute(
            """
            INSERT INTO feeds (feed_id, account_id, created_at, updated_at, text)
            VALUES ($1, $2, $3, $4, $5)
            """,
            feed.feed_id,
            feed.account_id,
            feed.created_at,
            feed.updated_at,
            feed.text,
        )

    async def update(self, feed: feed_entity.Feed) -> None:
        await self.conn.execute(
            """
            UPDATE feeds
            SET account_id = $2, created_at = $3, updated_at = $4, text = $5
            WHERE feed_id = $1
            """,
            feed.feed_id,
            feed.account_id,
            feed.created_at,
            feed.updated_at,
            feed.text,
        )
        # Unlink all images from this feed, then link/upsert only those in feed.images (batch)
        await self.conn.execute(
            "UPDATE images SET feed_id = NULL WHERE feed_id = $1",
            feed.feed_id,
        )
        if feed.images:
            image_ids = [img.image_id for img in feed.images]
            feed_ids = [feed.feed_id] * len(feed.images)
            uploaders = [img.uploader for img in feed.images]
            urls = [img.url for img in feed.images]
            blurhashes = [img.blurhash for img in feed.images]
            uploaded_ats = [img.uploaded_at for img in feed.images]
            orders = [img.order for img in feed.images]
            await self.conn.execute(
                """
                INSERT INTO images (image_id, feed_id, uploader, url, blurhash, uploaded_at, "order")
                SELECT * FROM unnest(
                    $1::uuid[], $2::uuid[], $3::text[], $4::text[], $5::text[],
                    $6::timestamptz[], $7::int[]
                ) AS t(image_id, feed_id, uploader, url, blurhash, uploaded_at, "order")
                ON CONFLICT (image_id) DO UPDATE SET
                    feed_id = EXCLUDED.feed_id,
                    uploader = EXCLUDED.uploader,
                    url = EXCLUDED.url,
                    blurhash = EXCLUDED.blurhash,
                    uploaded_at = EXCLUDED.uploaded_at,
                    "order" = EXCLUDED."order"
                """,
                image_ids,
                feed_ids,
                uploaders,
                urls,
                blurhashes,
                uploaded_ats,
                orders,
            )

    async def _fetch_images_by_feed_ids(
        self,
        feed_ids: list[uuid.UUID],
    ) -> dict[uuid.UUID, list[images_entity.Image]]:
        """Load all images for given feed_ids in one query; returns feed_id -> list[Image]."""
        if not feed_ids:
            return {}
        rows = await self.conn.fetch(
            """
            SELECT image_id, feed_id, uploader, url, blurhash, uploaded_at, "order"
            FROM images WHERE feed_id = ANY($1::uuid[]) ORDER BY feed_id, "order"
            """,
            feed_ids,
        )
        by_feed: dict[uuid.UUID, list[images_entity.Image]] = {
            fid: [] for fid in feed_ids
        }
        for r in rows:
            by_feed[r["feed_id"]].append(_row_to_image(r))
        return by_feed

    async def get_by_id(
        self,
        feed_id: uuid.UUID,
        current_account_id: str | None = None,
    ) -> feed_entity.Feed | None:
        row = await self.conn.fetchrow(
            _FEED_SELECT + " WHERE f.feed_id = $1",
            feed_id,
            current_account_id,
        )
        if row is None:
            return None
        images_by_feed = await self._fetch_images_by_feed_ids([feed_id])
        images = images_by_feed.get(feed_id, [])
        return _row_to_feed(row, images)

    async def get_by_ids(
        self,
        feed_ids: list[uuid.UUID],
        current_account_id: str | None = None,
    ) -> list[feed_entity.Feed]:
        if not feed_ids:
            return []
        rows = await self.conn.fetch(
            _FEED_SELECT + " WHERE f.feed_id = ANY($1::uuid[])",
            feed_ids,
            current_account_id,
        )
        images_by_feed = await self._fetch_images_by_feed_ids(
            [r["feed_id"] for r in rows],
        )
        result = []
        for row in rows:
            images = images_by_feed.get(row["feed_id"], [])
            result.append(_row_to_feed(row, images))
        return result

    async def get_account_feeds(
        self,
        account_id: str,
        limit: int = 100,
        offset: int = 0,
        current_account_id: str | None = None,
    ) -> tuple[list[feed_entity.Feed], int]:
        rows = await self.conn.fetch(
            _FEED_SELECT_WITH_TOTAL
            + " WHERE f.account_id = $1 ORDER BY f.created_at DESC LIMIT $3 OFFSET $4",
            account_id,
            current_account_id,
            limit,
            offset,
        )
        if not rows:
            return ([], 0)
        total_count = int(rows[0]["total_count"])
        images_by_feed = await self._fetch_images_by_feed_ids(
            [r["feed_id"] for r in rows],
        )
        result = []
        for row in rows:
            images = images_by_feed.get(row["feed_id"], [])
            result.append(_row_to_feed(row, images))
        return (result, total_count)

    async def count_feeds(self, account_id: str) -> int:
        r = await self.conn.fetchval(
            "SELECT count(*) FROM feeds WHERE account_id = $1",
            account_id,
        )
        return int(r) if r is not None else 0

    async def delete(self, feed_id: uuid.UUID) -> None:
        await self.conn.execute("DELETE FROM feeds WHERE feed_id = $1", feed_id)

    async def get_account_info_counts(self, account_id: str) -> tuple[int, int, int]:
        row = await self.conn.fetchrow(
            """
            SELECT
                (SELECT count(*)::int FROM followers WHERE follow_for = $1) AS followers_count,
                (SELECT count(*)::int FROM followers WHERE follower = $1) AS following_count,
                (SELECT count(*)::int FROM feeds WHERE account_id = $1) AS feeds_count
            """,
            account_id,
        )
        if row is None:
            return (0, 0, 0)
        return (
            int(row["followers_count"]) if row["followers_count"] is not None else 0,
            int(row["following_count"]) if row["following_count"] is not None else 0,
            int(row["feeds_count"]) if row["feeds_count"] is not None else 0,
        )

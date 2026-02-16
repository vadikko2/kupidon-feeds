import uuid

from domain.entities import like as like_entity
from infrastructure.persistent.postgres.base import BaseRepository
from service.interfaces.repositories import likes as likes_interface


def _row_to_like(row) -> like_entity.Like:
    return like_entity.Like(
        feed_id=row["feed_id"],
        account_id=row["account_id"],
        liked_at=row["liked_at"],
    )


class PostgresLikesRepository(BaseRepository, likes_interface.ILikesRepository):
    async def add(self, like: like_entity.Like) -> None:
        await self.conn.execute(
            """
            INSERT INTO likes (feed_id, account_id, liked_at)
            VALUES ($1, $2, $3)
            """,
            like.feed_id,
            like.account_id,
            like.liked_at,
        )

    async def delete(self, feed_id: uuid.UUID, account_id: str) -> None:
        await self.conn.execute(
            "DELETE FROM likes WHERE feed_id = $1 AND account_id = $2",
            feed_id,
            account_id,
        )

    async def get_by_feed_id(
        self,
        feed_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> likes_interface.GetLikesResult:
        rows = await self.conn.fetch(
            """
            SELECT feed_id, account_id, liked_at, total_count
            FROM (
                SELECT feed_id, account_id, liked_at,
                       count(*) OVER () AS total_count
                FROM likes WHERE feed_id = $1
            ) sub
            ORDER BY liked_at DESC
            LIMIT $2 OFFSET $3
            """,
            feed_id,
            limit,
            offset,
        )
        total_count = int(rows[0]["total_count"]) if rows else 0
        return (total_count, [_row_to_like(r) for r in rows])

    async def has_like(self, feed_id: uuid.UUID, account_id: str) -> bool:
        row = await self.conn.fetchrow(
            "SELECT 1 FROM likes WHERE feed_id = $1 AND account_id = $2",
            feed_id,
            account_id,
        )
        return row is not None

    async def count_by_feed_id(
        self,
        feed_id: uuid.UUID,
    ) -> likes_interface.TotalLikesCount:
        r = await self.conn.fetchval(
            "SELECT count(*) FROM likes WHERE feed_id = $1",
            feed_id,
        )
        return int(r) if r is not None else 0

    async def get_by_feed_id_and_account_id(
        self,
        feed_id: uuid.UUID,
        account_id: str,
    ) -> like_entity.Like | None:
        row = await self.conn.fetchrow(
            """
            SELECT feed_id, account_id, liked_at
            FROM likes WHERE feed_id = $1 AND account_id = $2
            """,
            feed_id,
            account_id,
        )
        if row is None:
            return None
        return _row_to_like(row)

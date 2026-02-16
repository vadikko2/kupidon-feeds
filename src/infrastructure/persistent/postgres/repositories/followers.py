from domain.entities import follower as follower_entity
from infrastructure.persistent.postgres.base import BaseRepository
from service.interfaces.repositories import followers as followers_interface


def _row_to_follower(row) -> follower_entity.Follower:
    return follower_entity.Follower(
        follower=row["follower"],
        follow_for=row["follow_for"],
        followed_at=row["followed_at"],
    )


class PostgresFollowersRepository(
    BaseRepository,
    followers_interface.IFollowersRepository,
):
    async def add(self, follower: follower_entity.Follower) -> None:
        await self.conn.execute(
            """
            INSERT INTO followers (follower, follow_for, followed_at)
            VALUES ($1, $2, $3)
            """,
            follower.follower,
            follower.follow_for,
            follower.followed_at,
        )

    async def delete(self, follower: str, follow_for: str) -> None:
        await self.conn.execute(
            "DELETE FROM followers WHERE follower = $1 AND follow_for = $2",
            follower,
            follow_for,
        )

    async def has_follow(self, follower: str, follow_for: str) -> bool:
        row = await self.conn.fetchrow(
            "SELECT 1 FROM followers WHERE follower = $1 AND follow_for = $2",
            follower,
            follow_for,
        )
        return row is not None

    async def get_follow(
        self,
        follower: str,
        follow_for: str,
    ) -> follower_entity.Follower | None:
        row = await self.conn.fetchrow(
            """
            SELECT follower, follow_for, followed_at
            FROM followers WHERE follower = $1 AND follow_for = $2
            """,
            follower,
            follow_for,
        )
        if row is None:
            return None
        return _row_to_follower(row)

    async def get_followers(
        self,
        account_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[follower_entity.Follower], int]:
        rows = await self.conn.fetch(
            """
            SELECT follower, follow_for, followed_at, total_count
            FROM (
                SELECT follower, follow_for, followed_at,
                       count(*) OVER () AS total_count
                FROM followers WHERE follow_for = $1
            ) sub
            ORDER BY followed_at DESC
            LIMIT $2 OFFSET $3
            """,
            account_id,
            limit,
            offset,
        )
        total_count = int(rows[0]["total_count"]) if rows else 0
        return ([_row_to_follower(r) for r in rows], total_count)

    async def get_following(
        self,
        account_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[follower_entity.Follower], int]:
        rows = await self.conn.fetch(
            """
            SELECT follower, follow_for, followed_at, total_count
            FROM (
                SELECT follower, follow_for, followed_at,
                       count(*) OVER () AS total_count
                FROM followers WHERE follower = $1
            ) sub
            ORDER BY followed_at DESC
            LIMIT $2 OFFSET $3
            """,
            account_id,
            limit,
            offset,
        )
        total_count = int(rows[0]["total_count"]) if rows else 0
        return ([_row_to_follower(r) for r in rows], total_count)

    async def count_followers(self, account_id: str) -> int:
        r = await self.conn.fetchval(
            "SELECT count(*) FROM followers WHERE follow_for = $1",
            account_id,
        )
        return int(r) if r is not None else 0

    async def count_following(self, account_id: str) -> int:
        r = await self.conn.fetchval(
            "SELECT count(*) FROM followers WHERE follower = $1",
            account_id,
        )
        return int(r) if r is not None else 0

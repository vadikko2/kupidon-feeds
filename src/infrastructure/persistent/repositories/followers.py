import sqlalchemy
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities import follower as follower_entity
from infrastructure.persistent.orm import FollowerORM
from service.interfaces.repositories import followers as followers_interface


class SQLAlchemyFollowersRepository(followers_interface.IFollowersRepository):
    """
    SQLAlchemy implementation of followers repository
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    def _orm_to_entity(self, follower_orm: FollowerORM) -> follower_entity.Follower:
        """
        Converts ORM model to domain entity
        """
        return follower_entity.Follower(
            follower=follower_orm.follower,  # type: ignore[arg-type]
            follow_for=follower_orm.follow_for,  # type: ignore[arg-type]
            followed_at=follower_orm.followed_at,  # type: ignore[arg-type]
        )

    async def add(self, follower: follower_entity.Follower) -> None:
        """
        Adds new follower
        """
        follower_orm = FollowerORM(
            follower=follower.follower,
            follow_for=follower.follow_for,
            followed_at=follower.followed_at,
        )
        self._session.add(follower_orm)

    async def delete(self, follower: str, follow_for: str) -> None:
        """
        Deletes follower
        """
        stmt = delete(FollowerORM).where(
            FollowerORM.follower == follower,
            FollowerORM.follow_for == follow_for,
        )
        await self._session.execute(stmt)
        # Flush sends DELETE statement to the database (but doesn't commit)
        # The handler will call commit() after this method returns
        await self._session.flush()

    async def has_follow(self, follower: str, follow_for: str) -> bool:
        """
        Checks if follower follows follow_for
        """
        stmt = select(FollowerORM).filter(
            FollowerORM.follower == follower,
            FollowerORM.follow_for == follow_for,
        )
        result = await self._session.execute(stmt)
        follower_orm = result.scalar_one_or_none()

        return follower_orm is not None

    async def get_follow(
        self,
        follower: str,
        follow_for: str,
    ) -> follower_entity.Follower | None:
        """
        Returns follower entity if exists, None otherwise
        """
        stmt = select(FollowerORM).filter(
            FollowerORM.follower == follower,
            FollowerORM.follow_for == follow_for,
        )
        result = await self._session.execute(stmt)
        follower_orm = result.scalar_one_or_none()

        if follower_orm is None:
            return None

        return self._orm_to_entity(follower_orm)

    async def get_followers(
        self,
        account_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[follower_entity.Follower]:
        """
        Returns followers (who follows account_id)
        """
        stmt = (
            select(FollowerORM)
            .filter(FollowerORM.follow_for == account_id)
            .order_by(FollowerORM.followed_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        followers_orm = result.scalars().all()

        return [self._orm_to_entity(follower_orm) for follower_orm in followers_orm]

    async def get_following(
        self,
        account_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[follower_entity.Follower]:
        """
        Returns following (who account_id follows)
        """
        stmt = (
            select(FollowerORM)
            .filter(FollowerORM.follower == account_id)
            .order_by(FollowerORM.followed_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        following_orm = result.scalars().all()

        return [self._orm_to_entity(follower_orm) for follower_orm in following_orm]

    async def count_followers(self, account_id: str) -> int:
        """
        Counts followers
        """
        stmt = select(sqlalchemy.func.count(FollowerORM.follower)).filter(
            FollowerORM.follow_for == account_id,
        )
        result = await self._session.execute(stmt)
        count = result.scalar()

        return count or 0

    async def count_following(self, account_id: str) -> int:
        """
        Counts following
        """
        stmt = select(sqlalchemy.func.count(FollowerORM.follow_for)).filter(
            FollowerORM.follower == account_id,
        )
        result = await self._session.execute(stmt)
        count = result.scalar()

        return count or 0

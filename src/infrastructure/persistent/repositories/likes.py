import uuid

import sqlalchemy
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities import like as like_entity
from infrastructure.persistent.orm import LikeORM
from service.interfaces.repositories import likes as likes_interface


class SQLAlchemyLikesRepository(likes_interface.ILikesRepository):
    """
    SQLAlchemy implementation of likes repository
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    def _orm_to_entity(self, like_orm: LikeORM) -> like_entity.Like:
        """
        Converts ORM model to domain entity
        """
        return like_entity.Like(
            feed_id=like_orm.feed_id,  # type: ignore[arg-type]
            account_id=like_orm.account_id,  # type: ignore[arg-type]
            liked_at=like_orm.liked_at,  # type: ignore[arg-type]
        )

    async def add(self, like: like_entity.Like) -> None:
        """
        Add new like for feed
        """
        like_orm = LikeORM(
            feed_id=like.feed_id,
            account_id=like.account_id,
            liked_at=like.liked_at,
        )
        self._session.add(like_orm)

    async def delete(self, feed_id: uuid.UUID, account_id: str) -> None:
        """
        Delete feed like
        """
        stmt = delete(LikeORM).where(
            LikeORM.feed_id == feed_id,
            LikeORM.account_id == account_id,
        )
        await self._session.execute(stmt)

    async def get_by_feed_id(
        self,
        feed_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> likes_interface.GetLikesResult:
        """
        Returns feed likes
        """
        # Get total count
        count_stmt = select(sqlalchemy.func.count(LikeORM.feed_id)).filter(
            LikeORM.feed_id == feed_id,
        )
        count_result = await self._session.execute(count_stmt)
        total_count = count_result.scalar() or 0

        # Get paginated likes
        stmt = (
            select(LikeORM)
            .filter(LikeORM.feed_id == feed_id)
            .order_by(LikeORM.liked_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        likes_orm = result.scalars().all()

        likes = [self._orm_to_entity(like_orm) for like_orm in likes_orm]

        return (total_count, likes)

    async def has_like(self, feed_id: uuid.UUID, account_id: str) -> bool:
        """
        Checks if user has liked the feed
        """
        stmt = select(LikeORM).filter(
            LikeORM.feed_id == feed_id,
            LikeORM.account_id == account_id,
        )
        result = await self._session.execute(stmt)
        like_orm = result.scalar_one_or_none()

        return like_orm is not None

    async def count_by_feed_id(
        self,
        feed_id: uuid.UUID,
    ) -> likes_interface.TotalLikesCount:
        """
        Returns total likes count for feed
        """
        stmt = select(sqlalchemy.func.count(LikeORM.feed_id)).filter(
            LikeORM.feed_id == feed_id,
        )
        result = await self._session.execute(stmt)
        count = result.scalar()

        return count or 0

    async def get_by_feed_id_and_account_id(
        self,
        feed_id: uuid.UUID,
        account_id: str,
    ) -> like_entity.Like | None:
        """
        Returns like by feed_id and account_id if exists
        """
        stmt = select(LikeORM).filter(
            LikeORM.feed_id == feed_id,
            LikeORM.account_id == account_id,
        )
        result = await self._session.execute(stmt)
        like_orm = result.scalar_one_or_none()

        if like_orm is None:
            return None

        return self._orm_to_entity(like_orm)

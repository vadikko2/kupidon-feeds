import typing

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from infrastructure.persistent.repositories import (
    feeds as feeds_repository,
    followers as followers_repository,
    images as images_repository,
    likes as likes_repository,
    views as views_repository,
)
from service.interfaces import unit_of_work as unit_of_work_interface


class SQLAlchemyUoW(unit_of_work_interface.UoW):
    """
    SQLAlchemy implementation of Unit of Work
    """

    feeds_repository: feeds_repository.SQLAlchemyFeedsRepository  # type: ignore[misc]
    images_repository: images_repository.SQLAlchemyImagesRepository  # type: ignore[misc]
    followers_repository: followers_repository.SQLAlchemyFollowersRepository  # type: ignore[misc]
    likes_repository: likes_repository.SQLAlchemyLikesRepository  # type: ignore[misc]
    views_repository: views_repository.SQLAlchemyViewsRepository  # type: ignore[misc]

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ):
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    async def __aenter__(self) -> typing.Self:
        """
        Creates a new session and initializes repositories
        """
        self._session = self._session_factory()

        self.feeds_repository = feeds_repository.SQLAlchemyFeedsRepository(
            self._session,
        )
        self.images_repository = images_repository.SQLAlchemyImagesRepository(
            self._session,
        )
        self.followers_repository = followers_repository.SQLAlchemyFollowersRepository(
            self._session,
        )
        self.likes_repository = likes_repository.SQLAlchemyLikesRepository(
            self._session,
        )
        self.views_repository = views_repository.SQLAlchemyViewsRepository(
            self._session,
        )

        return self

    async def commit(self) -> None:
        """
        Commits the current transaction
        """
        if self._session is not None:
            await self._session.commit()

    async def rollback(self) -> None:
        """
        Rolls back the current transaction
        """
        if self._session is not None:
            await self._session.rollback()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Closes the session
        Only rolls back if there was an exception and transaction is still active
        """
        if self._session is not None:
            # Only rollback if there was an exception and the session is still active
            if exc_type is not None:
                try:
                    await self._session.rollback()
                except Exception:
                    pass  # Ignore rollback errors if session is already closed

            await self._session.close()
            self._session = None

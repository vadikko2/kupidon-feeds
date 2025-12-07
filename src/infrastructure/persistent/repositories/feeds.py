import uuid

import sqlalchemy
from sqlalchemy import orm, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities import feed as feed_entity, images as images_entity
from infrastructure.persistent.orm import (
    FeedORM,
    ImageORM,
    LikeORM,
    ViewORM,
    FollowerORM,
)
from service import exceptions
from service.interfaces.repositories import feeds as feeds_interface


class SQLAlchemyFeedsRepository(feeds_interface.IFeedsRepository):
    """
    SQLAlchemy implementation of feeds repository
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    def _orm_to_entity(
        self,
        feed_orm: FeedORM,
        current_account_id: str | None = None,
        likes_count: int | None = None,
        views_count: int | None = None,
        has_followed: bool | None = None,
        has_liked: bool | None = None,
    ) -> feed_entity.Feed:
        """
        Converts ORM model to domain entity
        """
        images = [
            images_entity.Image(
                image_id=img.image_id,
                feed_id=img.feed_id,
                uploader=img.uploader,
                url=img.url,
                blurhash=img.blurhash,
                uploaded_at=img.uploaded_at,
                order=img.order,
            )
            for img in feed_orm.images
        ]

        # Используем переданные значения или вычисляем из relationship
        if likes_count is None:
            likes_count = len(feed_orm.likes) if hasattr(feed_orm, "likes") else 0

        if views_count is None:
            views_count = len(feed_orm.views) if hasattr(feed_orm, "views") else 0

        # Используем переданные значения has_followed и has_liked
        # Если они не переданы, устанавливаем значения по умолчанию
        if has_followed is None:
            has_followed = False

        if has_liked is None:
            has_liked = False

        return feed_entity.Feed(
            feed_id=feed_orm.feed_id,  # type: ignore[arg-type]
            account_id=feed_orm.account_id,  # type: ignore[arg-type]
            has_followed=has_followed,
            has_liked=has_liked,
            created_at=feed_orm.created_at,  # type: ignore[arg-type]
            updated_at=feed_orm.updated_at,  # type: ignore[arg-type]
            text=feed_orm.text,  # type: ignore[arg-type]
            images=images,
            likes_count=likes_count or 0,
            views_count=views_count or 0,
        )

    def _entity_to_orm(self, feed: feed_entity.Feed) -> FeedORM:
        """
        Converts domain entity to ORM model
        """
        feed_orm = FeedORM(
            feed_id=feed.feed_id,
            account_id=feed.account_id,
            created_at=feed.created_at,
            updated_at=feed.updated_at,
            text=feed.text,
        )

        # Add images
        for img in feed.images:
            image_orm = ImageORM(
                image_id=img.image_id,
                feed_id=img.feed_id,
                uploader=img.uploader,
                url=img.url,
                blurhash=img.blurhash,
                uploaded_at=img.uploaded_at,
                order=img.order,
            )
            feed_orm.images.append(image_orm)

        return feed_orm

    async def add(self, feed: feed_entity.Feed) -> None:
        """
        Adds new feed into storage
        :raises service.exceptions.FeedAlreadyExists:
        """
        existing = await self.get_by_id(feed.feed_id)
        if existing is not None:
            raise exceptions.FeedAlreadyExists(feed_id=feed.feed_id)

        feed_orm = FeedORM(
            feed_id=feed.feed_id,
            account_id=feed.account_id,
            created_at=feed.created_at,
            updated_at=feed.updated_at,
            text=feed.text,
        )

        # Don't link images here - they will be updated separately via images_repository.update()
        # Linking them here would cause duplicate insert attempts

        self._session.add(feed_orm)

    async def update(self, feed: feed_entity.Feed) -> None:
        """
        Updates feed in storage
        """
        # Load feed with images using selectinload to avoid lazy loading issues
        stmt = (
            select(FeedORM)
            .options(orm.selectinload(FeedORM.images))
            .filter(FeedORM.feed_id == feed.feed_id)
        )
        result = await self._session.execute(stmt)
        feed_orm = result.unique().scalar_one_or_none()

        if feed_orm is None:
            raise exceptions.FeedNotFound(feed_id=feed.feed_id)

        # Update feed fields
        feed_orm.account_id = feed.account_id  # type: ignore[assignment]
        feed_orm.created_at = feed.created_at  # type: ignore[assignment]
        feed_orm.updated_at = feed.updated_at  # type: ignore[assignment]
        feed_orm.text = feed.text  # type: ignore[assignment]

        # Update images - remove old ones and add new ones
        # Get existing image IDs
        existing_image_ids = {img.image_id for img in feed_orm.images}
        new_image_ids = {img.image_id for img in feed.images}

        # Remove images that are no longer in the feed
        images_to_remove = [
            img for img in feed_orm.images if img.image_id not in new_image_ids
        ]
        for img in images_to_remove:
            feed_orm.images.remove(img)

        # Add or update images
        for img in feed.images:
            if img.image_id in existing_image_ids:
                # Update existing image that's already in the collection
                existing_img = next(
                    (i for i in feed_orm.images if i.image_id == img.image_id),
                    None,
                )
                if existing_img:
                    existing_img.feed_id = img.feed_id
                    existing_img.uploader = img.uploader
                    existing_img.url = img.url
                    existing_img.blurhash = img.blurhash
                    existing_img.uploaded_at = img.uploaded_at
                    existing_img.order = img.order
            else:
                # Load existing image from database or create new one
                image_orm = await self._session.get(ImageORM, img.image_id)
                if image_orm is None:
                    # Image doesn't exist, create new one
                    image_orm = ImageORM(
                        image_id=img.image_id,
                        feed_id=img.feed_id,
                        uploader=img.uploader,
                        url=img.url,
                        blurhash=img.blurhash,
                        uploaded_at=img.uploaded_at,
                        order=img.order,
                    )
                    self._session.add(image_orm)
                else:
                    # Image exists, update it
                    image_orm.feed_id = img.feed_id  # type: ignore[assignment]
                    image_orm.uploader = img.uploader  # type: ignore[assignment]
                    image_orm.url = img.url  # type: ignore[assignment]
                    image_orm.blurhash = img.blurhash  # type: ignore[assignment]
                    image_orm.uploaded_at = img.uploaded_at  # type: ignore[assignment]
                    image_orm.order = img.order  # type: ignore[assignment]

                feed_orm.images.append(image_orm)

    async def get_by_id(
        self,
        feed_id: uuid.UUID,
        current_account_id: str | None = None,
    ) -> feed_entity.Feed | None:
        """
        Returns feed by id
        """
        # Подзапрос для подсчета лайков
        likes_count_subquery = (
            select(sqlalchemy.func.count(LikeORM.feed_id))
            .filter(LikeORM.feed_id == FeedORM.feed_id)
            .scalar_subquery()
        )

        # Подзапрос для подсчета просмотров
        views_count_subquery = (
            select(sqlalchemy.func.count(ViewORM.feed_id))
            .filter(ViewORM.feed_id == FeedORM.feed_id)
            .scalar_subquery()
        )

        # Подзапрос для проверки has_followed (подписан ли current_account_id на автора поста)
        if current_account_id:
            has_followed_subquery = select(
                sqlalchemy.exists()
                .where(
                    FollowerORM.follower == current_account_id,
                    FollowerORM.follow_for == FeedORM.account_id,
                )
                .correlate(FeedORM),
            ).scalar_subquery()
        else:
            has_followed_subquery = select(
                sqlalchemy.literal(False).cast(sqlalchemy.Boolean),
            ).scalar_subquery()

        # Подзапрос для проверки has_liked (лайкнул ли current_account_id этот пост)
        if current_account_id:
            has_liked_subquery = select(
                sqlalchemy.exists()
                .where(
                    LikeORM.feed_id == FeedORM.feed_id,
                    LikeORM.account_id == current_account_id,
                )
                .correlate(FeedORM),
            ).scalar_subquery()
        else:
            has_liked_subquery = select(
                sqlalchemy.literal(False).cast(sqlalchemy.Boolean),
            ).scalar_subquery()

        stmt = (
            select(
                FeedORM,
                likes_count_subquery.label("calculated_likes_count"),
                views_count_subquery.label("calculated_views_count"),
                has_followed_subquery.label("calculated_has_followed"),
                has_liked_subquery.label("calculated_has_liked"),
            )
            .options(orm.joinedload(FeedORM.images))
            .filter(FeedORM.feed_id == feed_id)
        )
        result = await self._session.execute(stmt)
        row = result.unique().first()

        if row is None:
            return None

        feed_orm, likes_count, views_count, has_followed, has_liked = row
        likes_count_value = int(likes_count) if likes_count is not None else 0
        views_count_value = int(views_count) if views_count is not None else 0
        has_followed_value = bool(has_followed) if has_followed is not None else False
        has_liked_value = bool(has_liked) if has_liked is not None else False
        return self._orm_to_entity(
            feed_orm,
            current_account_id=current_account_id,
            likes_count=likes_count_value,
            views_count=views_count_value,
            has_followed=has_followed_value,
            has_liked=has_liked_value,
        )

    async def get_by_ids(
        self,
        feed_ids: list[uuid.UUID],
        current_account_id: str | None = None,
    ) -> list[feed_entity.Feed]:
        """
        Returns feeds by ids
        """
        if not feed_ids:
            return []

        # Подзапрос для подсчета лайков
        likes_count_subquery = (
            select(sqlalchemy.func.count(LikeORM.feed_id))
            .filter(LikeORM.feed_id == FeedORM.feed_id)
            .scalar_subquery()
        )

        # Подзапрос для подсчета просмотров
        views_count_subquery = (
            select(sqlalchemy.func.count(ViewORM.feed_id))
            .filter(ViewORM.feed_id == FeedORM.feed_id)
            .scalar_subquery()
        )

        # Подзапрос для проверки has_followed (подписан ли current_account_id на автора поста)
        if current_account_id:
            has_followed_subquery = select(
                sqlalchemy.exists()
                .where(
                    FollowerORM.follower == current_account_id,
                    FollowerORM.follow_for == FeedORM.account_id,
                )
                .correlate(FeedORM),
            ).scalar_subquery()
        else:
            has_followed_subquery = select(
                sqlalchemy.literal(False).cast(sqlalchemy.Boolean),
            ).scalar_subquery()

        # Подзапрос для проверки has_liked (лайкнул ли current_account_id этот пост)
        if current_account_id:
            has_liked_subquery = select(
                sqlalchemy.exists()
                .where(
                    LikeORM.feed_id == FeedORM.feed_id,
                    LikeORM.account_id == current_account_id,
                )
                .correlate(FeedORM),
            ).scalar_subquery()
        else:
            has_liked_subquery = select(
                sqlalchemy.literal(False).cast(sqlalchemy.Boolean),
            ).scalar_subquery()

        stmt = (
            select(
                FeedORM,
                likes_count_subquery.label("calculated_likes_count"),
                views_count_subquery.label("calculated_views_count"),
                has_followed_subquery.label("calculated_has_followed"),
                has_liked_subquery.label("calculated_has_liked"),
            )
            .options(orm.joinedload(FeedORM.images))
            .filter(FeedORM.feed_id.in_(feed_ids))
        )
        result = await self._session.execute(stmt)
        rows = result.unique().all()

        return [
            self._orm_to_entity(
                feed_orm,
                current_account_id=current_account_id,
                likes_count=int(likes_count) if likes_count is not None else 0,
                views_count=int(views_count) if views_count is not None else 0,
                has_followed=bool(has_followed) if has_followed is not None else False,
                has_liked=bool(has_liked) if has_liked is not None else False,
            )
            for feed_orm, likes_count, views_count, has_followed, has_liked in rows
        ]

    async def get_account_feeds(
        self,
        account_id: str,
        limit: int = 100,
        offset: int = 0,
        current_account_id: str | None = None,
    ) -> list[feed_entity.Feed]:
        """
        Returns account feeds
        """
        # Подзапрос для подсчета лайков
        likes_count_subquery = (
            select(sqlalchemy.func.count(LikeORM.feed_id))
            .filter(LikeORM.feed_id == FeedORM.feed_id)
            .scalar_subquery()
        )

        # Подзапрос для подсчета просмотров
        views_count_subquery = (
            select(sqlalchemy.func.count(ViewORM.feed_id))
            .filter(ViewORM.feed_id == FeedORM.feed_id)
            .scalar_subquery()
        )

        # Подзапрос для проверки has_followed (подписан ли current_account_id на автора поста)
        if current_account_id:
            has_followed_subquery = select(
                sqlalchemy.exists()
                .where(
                    FollowerORM.follower == current_account_id,
                    FollowerORM.follow_for == FeedORM.account_id,
                )
                .correlate(FeedORM),
            ).scalar_subquery()
        else:
            has_followed_subquery = select(
                sqlalchemy.literal(False).cast(sqlalchemy.Boolean),
            ).scalar_subquery()

        # Подзапрос для проверки has_liked (лайкнул ли current_account_id этот пост)
        if current_account_id:
            has_liked_subquery = select(
                sqlalchemy.exists()
                .where(
                    LikeORM.feed_id == FeedORM.feed_id,
                    LikeORM.account_id == current_account_id,
                )
                .correlate(FeedORM),
            ).scalar_subquery()
        else:
            has_liked_subquery = select(
                sqlalchemy.literal(False).cast(sqlalchemy.Boolean),
            ).scalar_subquery()

        stmt = (
            select(
                FeedORM,
                likes_count_subquery.label("calculated_likes_count"),
                views_count_subquery.label("calculated_views_count"),
                has_followed_subquery.label("calculated_has_followed"),
                has_liked_subquery.label("calculated_has_liked"),
            )
            .options(orm.joinedload(FeedORM.images))
            .filter(FeedORM.account_id == account_id)
            .order_by(FeedORM.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        rows = result.unique().all()

        return [
            self._orm_to_entity(
                feed_orm,
                current_account_id=current_account_id,
                likes_count=int(likes_count) if likes_count is not None else 0,
                views_count=int(views_count) if views_count is not None else 0,
                has_followed=bool(has_followed) if has_followed is not None else False,
                has_liked=bool(has_liked) if has_liked is not None else False,
            )
            for feed_orm, likes_count, views_count, has_followed, has_liked in rows
        ]

    async def count_feeds(self, account_id: str) -> int:
        """
        Returns account feeds count
        """
        stmt = select(sqlalchemy.func.count(FeedORM.feed_id)).filter(
            FeedORM.account_id == account_id,
        )
        result = await self._session.execute(stmt)
        count = result.scalar()

        return count or 0

    async def delete(self, feed_id: uuid.UUID) -> None:
        """
        Deletes feed by id
        Note: This method assumes the feed exists (checked by the handler).
        - Images will have feed_id set to NULL via DB foreign key constraint (ondelete="SET NULL")
        - Likes will be deleted via ORM cascade (cascade="all, delete-orphan")
        - Views will be deleted via ORM cascade (cascade="all, delete-orphan")
        """
        # Load feed with likes and views to ensure cascade deletion works
        # Images don't need to be loaded - they will be handled by DB foreign key constraint
        # We use selectinload to eagerly load relationships for cascade deletion
        stmt = (
            select(FeedORM)
            .options(
                orm.selectinload(FeedORM.likes),
                orm.selectinload(FeedORM.views),
            )
            .filter(FeedORM.feed_id == feed_id)
        )
        result = await self._session.execute(stmt)
        feed_orm = result.unique().scalar_one_or_none()

        if feed_orm is None:
            raise exceptions.FeedNotFound(feed_id=feed_id)

        # Delete the feed
        # - Likes will be deleted automatically via ORM cascade (cascade="all, delete-orphan")
        # - Views will be deleted automatically via ORM cascade (cascade="all, delete-orphan")
        # - Images will have feed_id set to NULL automatically via DB foreign key constraint (ondelete="SET NULL")
        # Note: session.delete() is synchronous and marks the object for deletion
        # The commit() in the handler will execute the DELETE statements
        await self._session.delete(feed_orm)  # pyright: ignore[reportUnusedCoroutine]

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities import images as images_entity
from infrastructure.persistent.orm import ImageORM
from service import exceptions
from service.interfaces.repositories import images as images_interface


class SQLAlchemyImagesRepository(images_interface.IImageRepository):
    """
    SQLAlchemy implementation of images repository
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    def _orm_to_entity(self, image_orm: ImageORM) -> images_entity.Image:
        """
        Converts ORM model to domain entity
        """
        return images_entity.Image(
            image_id=image_orm.image_id,  # type: ignore[arg-type]
            feed_id=image_orm.feed_id,  # type: ignore[arg-type]
            uploader=image_orm.uploader,  # type: ignore[arg-type]
            url=image_orm.url,  # type: ignore[arg-type]
            blurhash=image_orm.blurhash,  # type: ignore[arg-type]
            uploaded_at=image_orm.uploaded_at,  # type: ignore[arg-type]
            order=image_orm.order,  # type: ignore[arg-type]
        )

    async def add(self, image: images_entity.Image) -> None:
        """
        Saves new image info into storage
        :raises service.exceptions.ImageAlreadyExists:
        """
        existing = await self.get_by_id(image.image_id)
        if existing is not None:
            raise exceptions.ImageAlreadyExists(image_id=image.image_id)

        image_orm = ImageORM(
            image_id=image.image_id,
            feed_id=image.feed_id,
            uploader=image.uploader,
            url=image.url,
            blurhash=image.blurhash,
            uploaded_at=image.uploaded_at,
            order=image.order,
        )
        self._session.add(image_orm)

    async def get_by_id(self, image_id: uuid.UUID) -> images_entity.Image | None:
        """
        Returns image info by id from storage
        """
        image_orm = await self._session.get(ImageORM, image_id)
        if image_orm is None:
            return None

        return self._orm_to_entity(image_orm)

    async def get_many(self, *image_id: uuid.UUID) -> list[images_entity.Image]:
        """
        Returns many images by id
        """
        stmt = select(ImageORM).filter(ImageORM.image_id.in_(image_id))
        result = await self._session.execute(stmt)
        images_orm = result.scalars().all()

        return [self._orm_to_entity(img_orm) for img_orm in images_orm]

    async def update(self, *image: images_entity.Image):
        """
        Updates images by id
        :raises service.exceptions.ImageNotFound:
        """
        for img in image:
            image_orm = await self._session.get(ImageORM, img.image_id)
            if image_orm is None:
                raise exceptions.ImageNotFound(image_id=img.image_id)

            image_orm.feed_id = img.feed_id  # type: ignore[assignment]
            image_orm.uploader = img.uploader  # type: ignore[assignment]
            image_orm.url = img.url  # type: ignore[assignment]
            image_orm.blurhash = img.blurhash  # type: ignore[assignment]
            image_orm.uploaded_at = img.uploaded_at  # type: ignore[assignment]
            image_orm.order = img.order  # type: ignore[assignment]

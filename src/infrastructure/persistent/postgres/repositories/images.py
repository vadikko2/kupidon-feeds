import uuid

import asyncpg

from domain.entities import images as images_entity
from infrastructure.persistent.postgres.base import BaseRepository
from service import exceptions
from service.interfaces.repositories import images as images_interface


def _row_to_image(row: asyncpg.Record) -> images_entity.Image:
    return images_entity.Image(
        image_id=row["image_id"],
        feed_id=row["feed_id"],
        uploader=row["uploader"],
        url=row["url"],
        blurhash=row["blurhash"],
        uploaded_at=row["uploaded_at"],
        order=row["order"],
    )


class PostgresImagesRepository(BaseRepository, images_interface.IImageRepository):
    async def add(self, image: images_entity.Image) -> None:
        row = await self.conn.fetchrow(
            "SELECT 1 FROM images WHERE image_id = $1",
            image.image_id,
        )
        if row is not None:
            raise exceptions.ImageAlreadyExists(image_id=image.image_id)
        await self.conn.execute(
            """
            INSERT INTO images (image_id, feed_id, uploader, url, blurhash, uploaded_at, "order")
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            image.image_id,
            image.feed_id,
            image.uploader,
            image.url,
            image.blurhash,
            image.uploaded_at,
            image.order,
        )

    async def get_by_id(self, image_id: uuid.UUID) -> images_entity.Image | None:
        row = await self.conn.fetchrow(
            """
            SELECT image_id, feed_id, uploader, url, blurhash, uploaded_at, "order"
            FROM images WHERE image_id = $1
            """,
            image_id,
        )
        if row is None:
            return None
        return _row_to_image(row)

    async def get_many(self, *image_ids: uuid.UUID) -> list[images_entity.Image]:
        if not image_ids:
            return []
        rows = await self.conn.fetch(
            """
            SELECT image_id, feed_id, uploader, url, blurhash, uploaded_at, "order"
            FROM images WHERE image_id = ANY($1::uuid[])
            """,
            list(image_ids),
        )
        return [_row_to_image(r) for r in rows]

    async def update(self, *image: images_entity.Image) -> None:
        if not image:
            return
        image_ids = [img.image_id for img in image]
        feed_ids = [img.feed_id for img in image]
        uploaders = [img.uploader for img in image]
        urls = [img.url for img in image]
        blurhashes = [img.blurhash for img in image]
        uploaded_ats = [img.uploaded_at for img in image]
        orders = [img.order for img in image]
        await self.conn.execute(
            """
            UPDATE images AS i
            SET
                feed_id = d.feed_id,
                uploader = d.uploader,
                url = d.url,
                blurhash = d.blurhash,
                uploaded_at = d.uploaded_at,
                "order" = d."order"
            FROM (
                SELECT * FROM unnest(
                    $1::uuid[],
                    $2::uuid[],
                    $3::text[],
                    $4::text[],
                    $5::text[],
                    $6::timestamptz[],
                    $7::int[]
                ) AS t(image_id, feed_id, uploader, url, blurhash, uploaded_at, "order")
            ) AS d
            WHERE i.image_id = d.image_id
            """,
            image_ids,
            feed_ids,
            uploaders,
            urls,
            blurhashes,
            uploaded_ats,
            orders,
        )

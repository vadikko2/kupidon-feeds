import uuid

import orjson
from redis.asyncio import client

from domain.entities import images
from service import exceptions
from service.interfaces.repositories import images as images_interfaces


class RedisImagesRepository(images_interfaces.IImageRepository):
    KEY_PATTER = "image:{image_id}"

    def __init__(self, pipeline: client.Pipeline):
        self.pipeline = pipeline

    async def add(self, image: images.Image) -> None:
        key = self.KEY_PATTER.format(image_id=image.image_id)
        existed_coroutine = await self.pipeline.get(key)
        existed = (await existed_coroutine.execute())[0]
        if existed:
            raise exceptions.ImageAlreadyExists(image_id=image.image_id)

        coroutine = await self.pipeline.set(key, orjson.dumps(image.model_dump()))
        _ = (await coroutine.execute())[0]

    async def get_by_id(self, image_id: uuid.UUID) -> images.Image | None:
        key = self.KEY_PATTER.format(image_id=image_id)
        existed_coroutine = await self.pipeline.get(key)
        existed = (await existed_coroutine.execute())[0]
        if existed:
            return images.Image.model_validate(orjson.loads(existed))

    async def get_many(self, *image_id: uuid.UUID) -> list[images.Image]:
        images_list = []
        coroutine = await self.pipeline.mget(
            [self.KEY_PATTER.format(image_id=id_) for id_ in image_id],
        )
        rows = (await coroutine.execute())[0]
        for row in rows:
            if row is None:
                continue
            images_list.append(images.Image.model_validate(orjson.loads(row)))
        return images_list

    async def update(self, *image: images.Image):
        for im in image:
            key = self.KEY_PATTER.format(image_id=im.image_id)
            exists = await self.get_by_id(im.image_id)
            if not exists:
                raise exceptions.ImageNotFound(image_id=im.image_id)

            coroutine = await self.pipeline.set(key, orjson.dumps(im.model_dump()))
            _ = (await coroutine.execute())[0]

import io
import typing
import uuid

import cqrs
from cqrs.events import event

from domain.entities import images as images_entity
from service.helpers.image import blurhash, transcode
from service.interfaces import unit_of_work
from service.interfaces.storages import images_storage as images_storage_interface
from service.models.commands.images import upload_image


class UploadImageHandler(
    cqrs.RequestHandler[upload_image.UploadImage, upload_image.UploadImageResponse],
):
    def __init__(
        self,
        image_storage: images_storage_interface.ImagesStorage,
        uow: unit_of_work.UoW,
    ):
        self.image_storage = image_storage
        self.uow = uow
        self._events = []

    @property
    def events(self) -> typing.List[event.Event]:
        return []

    async def handle(
        self,
        request: upload_image.UploadImage,
    ) -> upload_image.UploadImageResponse:
        transcode_image = transcode.transcode_to_jpeg(io.BytesIO(request.image))
        transcode_image.seek(0)
        blurhash_value = blurhash.generate_blurhash(transcode_image)

        image_for_uploading = images_storage_interface.Image(
            image=transcode_image.read(),
            filename=request.filename or str(uuid.uuid4()),
        )
        [url] = await self.image_storage.upload(image_for_uploading)
        uploaded_image = images_entity.Image(
            image_id=uuid.uuid4(),
            uploader=request.uploader,
            url=url,
            blurhash=blurhash_value,
        )
        async with self.uow:
            await self.uow.images_repository.add(uploaded_image)
            await self.uow.commit()

        return upload_image.UploadImageResponse(image=uploaded_image)

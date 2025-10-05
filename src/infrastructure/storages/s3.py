import io
import logging

import boto3.session
from botocore import client

from infrastructure.storages import settings
from service.interfaces.storages import images_storage

logging.getLogger("botocore").setLevel(logging.ERROR)
logging.getLogger("s3transfer").setLevel(logging.ERROR)
logging.getLogger("boto3").setLevel(logging.ERROR)


class S3ImagesStorage(images_storage.ImagesStorage):
    def __init__(self):
        self.endpoint_url = settings.s3_settings.ENDPOINT_URL
        self.region_name = settings.s3_settings.REGION_NAME

        self.bucket_name = settings.s3_settings.BUCKET_NAME
        self.path_prefix = settings.s3_settings.PATH_PREFIX

        self.access_key_id = settings.s3_settings.ACCESS_KEY_ID
        self.secret_access_key = settings.s3_settings.SECRET_ACCESS_KEY

    def _generate_download_url(self, filename: str) -> str:
        return self.endpoint_url + "/" + self.bucket_name + "/" + filename

    async def upload_one(self, image: images_storage.Image) -> str:
        full_filename = (
            f"{self.path_prefix}/{image.filename}"
            if self.path_prefix
            else image.filename
        )
        session = boto3.session.Session()
        s3: client.BaseClient = session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            region_name=self.region_name,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
        )

        image_io = io.BytesIO(image.image)
        image_io.seek(0)
        s3.upload_fileobj(image_io, self.bucket_name, full_filename)
        return self._generate_download_url(full_filename)

    async def upload(self, *image: images_storage.Image) -> list[str]:
        urls = []
        for img in image:
            urls.append(await self.upload_one(img))
        return urls

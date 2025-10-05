import typing

import di
import redis.asyncio as redis
from di import dependent
from service.interfaces.storages import images_storage as images_storage_interface

from infrastructure.cache import redis as redis_cache
from infrastructure.services import iam_service
from infrastructure.storages import s3
from service.interfaces.services import iam_service as iam_service_interface

container = di.Container()

container.bind(
    di.bind_by_type(
        dependent.Dependent(iam_service.HttpIAMService, scope="request"),
        iam_service_interface.IAMService,
    ),
)

container.bind(
    di.bind_by_type(
        dependent.Dependent(redis_cache.RedisClientFactory, scope="request"),
        typing.Callable[[], redis.Redis],  # pyright: ignore[reportArgumentType]
    ),
)

container.bind(
    di.bind_by_type(
        dependent.Dependent(s3.S3ImagesStorage, scope="request"),
        images_storage_interface.ImagesStorage,
    ),
)

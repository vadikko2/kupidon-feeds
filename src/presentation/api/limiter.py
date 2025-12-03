import slowapi
from slowapi.util import get_remote_address

from infrastructure.cache import settings

limiter = slowapi.Limiter(
    get_remote_address,
    storage_uri=settings.redis_settings.redis_url,
)

import redis.asyncio as redis

from infrastructure.cache import settings

connection_pool = redis.ConnectionPool.from_url(settings.redis_settings.redis_url)


class RedisClientFactory:
    def __call__(self) -> redis.Redis:
        return redis.Redis(connection_pool=connection_pool)

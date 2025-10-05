import logging
import typing

import redis.asyncio as redis

from service.interfaces.cache import CacheService

logger = logging.getLogger(__name__)


class RedisCacheService(CacheService):
    """Redis implementation of CacheService."""

    def __init__(self, redis_factory: typing.Callable[[], redis.Redis]):
        self._redis_client = redis_factory()

    async def get(self, key: str) -> typing.Optional[bytes]:
        """Get value from Redis cache by key."""
        try:
            return await self._redis_client.get(key)
        except Exception as e:
            logger.error(f"Failed to get value from cache for key {key}: {e}")
            return None

    async def setex(self, key: str, ttl_seconds: int, value: bytes) -> None:
        """Set value in Redis cache with TTL."""
        try:
            await self._redis_client.setex(key, ttl_seconds, value)
        except Exception as e:
            logger.error(f"Failed to set value in cache for key {key}: {e}")
            raise

    async def delete(self, key: str) -> None:
        """Delete value from Redis cache by key."""
        try:
            await self._redis_client.delete(key)
        except Exception as e:
            logger.error(f"Failed to delete value from cache for key {key}: {e}")
            raise

    async def mget(self, keys: list[str]) -> list[typing.Optional[bytes]]:
        """Get multiple values from Redis cache by keys."""
        try:
            if not keys:
                return []
            async with self._redis_client.pipeline() as pipe:
                coroutine = await pipe.mget(keys)
                return (await coroutine.execute())[0]
        except Exception as e:
            logger.error(
                f"Failed to get multiple values from cache for keys {keys}: {e}",
            )
            return [None] * len(keys)

    async def mset(self, mapping: dict[str, bytes], ttl_seconds: int) -> None:
        """Set multiple values in Redis cache with TTL."""
        try:
            if not mapping:
                return

            # Use pipeline for atomic operation
            async with self._redis_client.pipeline() as pipe:
                # Set all values
                await pipe.mset(mapping)
                # Set TTL for all keys
                for key in mapping.keys():
                    await pipe.expire(key, ttl_seconds)
                await pipe.execute()
        except Exception as e:
            logger.error(f"Failed to set multiple values in cache: {e}")
            raise

    async def delete_by_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern from Redis cache."""
        try:
            # Find all keys matching the pattern
            keys = await self._redis_client.keys(pattern)
            if not keys:
                logger.info(f"No keys found matching pattern: {pattern}")
                return 0

            # Delete all matching keys
            deleted_count = await self._redis_client.delete(*keys)
            logger.info(f"Deleted {deleted_count} keys matching pattern: {pattern}")
            return deleted_count
        except Exception as e:
            logger.error(f"Failed to delete keys by pattern {pattern}: {e}")
            raise

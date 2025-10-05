import abc
import typing


class CacheService(abc.ABC):
    """Abstract interface for cache operations."""

    @abc.abstractmethod
    async def get(self, key: str) -> typing.Optional[bytes]:
        """
        Get value from cache by key.

        Args:
            key: Cache key

        Returns:
            Cached value as bytes or None if not found
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def setex(self, key: str, ttl_seconds: int, value: bytes) -> None:
        """
        Set value in cache with TTL.

        Args:
            key: Cache key
            ttl_seconds: Time to live in seconds
            value: Value to cache as bytes
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, key: str) -> None:
        """
        Delete value from cache by key.

        Args:
            key: Cache key
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def mget(self, keys: list[str]) -> list[typing.Optional[bytes]]:
        """
        Get multiple values from cache by keys.

        Args:
            keys: List of cache keys

        Returns:
            List of cached values as bytes or None if not found
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def mset(self, mapping: dict[str, bytes], ttl_seconds: int) -> None:
        """
        Set multiple values in cache with TTL.

        Args:
            mapping: Dictionary of key-value pairs
            ttl_seconds: Time to live in seconds
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def delete_by_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.

        Args:
            pattern: Redis pattern to match keys (e.g., "profiles_cache:*")

        Returns:
            Number of deleted keys
        """
        raise NotImplementedError

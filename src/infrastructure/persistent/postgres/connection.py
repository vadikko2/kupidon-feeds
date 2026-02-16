"""
Asyncpg connection pool for Postgres.
"""

import logging

import asyncpg

from infrastructure.persistent.settings import postgres_settings

logger = logging.getLogger(__name__)

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        raise RuntimeError(
            "Postgres connection pool is not initialized. Call init_pool() first.",
        )
    return _pool


async def init_pool() -> None:
    global _pool
    try:
        _pool = await asyncpg.create_pool(
            dsn=postgres_settings.dsn,
            min_size=postgres_settings.POOL_MIN_SIZE,
            max_size=postgres_settings.POOL_MAX_SIZE,
            command_timeout=60,
        )
    except Exception as e:
        logger.error("Failed to initialize Postgres pool: %s", e)
        raise


async def close_pool() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None

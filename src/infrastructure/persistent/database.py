"""
Database connection and session management with connection pooling
"""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from infrastructure.persistent.settings import database_settings


def create_engine() -> AsyncEngine:
    """
    Creates async SQLAlchemy engine with connection pool configuration
    """
    engine = create_async_engine(
        database_settings.URL,
        pool_size=database_settings.POOL_SIZE,
        max_overflow=database_settings.MAX_OVERFLOW,
        pool_timeout=database_settings.POOL_TIMEOUT,
        pool_recycle=database_settings.POOL_RECYCLE,
        pool_pre_ping=database_settings.POOL_PRE_PING,
        echo=database_settings.ECHO,
    )
    return engine


def create_session_factory(
    engine: AsyncEngine | None = None,
) -> async_sessionmaker[AsyncSession]:
    """
    Creates async session factory with proper configuration

    Args:
        engine: Optional engine instance. If not provided, a new one will be created.

    Returns:
        Configured async_sessionmaker instance
    """
    if engine is None:
        engine = create_engine()

    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    return session_factory


# Global engine instance (can be initialized on application startup)
_engine: AsyncEngine | None = None


def get_engine() -> AsyncEngine:
    """
    Gets or creates the global engine instance
    """
    global _engine
    if _engine is None:
        _engine = create_engine()
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    Gets or creates the global session factory instance
    """
    engine = get_engine()
    return create_session_factory(engine)


async def close_engine() -> None:
    """
    Closes the global engine and disposes of all connections in the pool
    Should be called on application shutdown
    """
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None

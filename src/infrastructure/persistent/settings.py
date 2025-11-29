import pydantic
import pydantic_settings
import dotenv

dotenv.load_dotenv()


class DatabaseSettings(pydantic_settings.BaseSettings):
    """
    Database connection settings
    """

    URL: str = pydantic.Field(
        default="postgresql+asyncpg://user:password@localhost:5432/dbname",
        description="Database connection URL",
    )
    POOL_SIZE: int = pydantic.Field(
        default=5,
        ge=1,
        le=100,
        description="Number of connections to maintain in the pool",
    )
    MAX_OVERFLOW: int = pydantic.Field(
        default=10,
        ge=0,
        le=100,
        description="Maximum number of connections to allow in addition to pool_size",
    )
    POOL_TIMEOUT: int = pydantic.Field(
        default=30,
        ge=1,
        description="Number of seconds to wait before giving up on getting a connection from the pool",
    )
    POOL_RECYCLE: int = pydantic.Field(
        default=3600,
        ge=1,
        description="Number of seconds after which a connection is recreated",
    )
    POOL_PRE_PING: bool = pydantic.Field(
        default=True,
        description="Enable connection health checks",
    )
    ECHO: bool = pydantic.Field(
        default=False,
        description="Enable SQL query logging",
    )

    model_config = pydantic_settings.SettingsConfigDict(env_prefix="DATABASE_")


database_settings = DatabaseSettings()

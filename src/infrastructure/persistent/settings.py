import pydantic_settings
from pydantic import Field
import dotenv

dotenv.load_dotenv()


class PostgresSettings(pydantic_settings.BaseSettings):
    """Postgres connection settings for asyncpg."""

    HOSTNAME: str = Field(default="localhost")
    PORT: int = Field(default=5432)
    DATABASE: str = Field(default="feeds")
    USER: str = Field(default="postgres")
    PASSWORD: str = Field(default="postgres")
    POOL_MIN_SIZE: int = Field(default=5, description="Min connections in pool")
    POOL_MAX_SIZE: int = Field(default=20, description="Max connections in pool")

    @property
    def dsn(self) -> str:
        return f"postgresql://{self.USER}:{self.PASSWORD}@{self.HOSTNAME}:{self.PORT}/{self.DATABASE}"

    model_config = pydantic_settings.SettingsConfigDict(env_prefix="POSTGRES_")


postgres_settings = PostgresSettings()

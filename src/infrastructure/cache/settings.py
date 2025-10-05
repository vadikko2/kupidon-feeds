import dotenv
import pydantic
import pydantic_settings

dotenv.load_dotenv()


class RedisSettings(pydantic_settings.BaseSettings):
    redis_url: str = pydantic.Field(default="notset")


redis_settings = RedisSettings()

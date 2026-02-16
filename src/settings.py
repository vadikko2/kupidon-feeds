import dotenv
import pydantic
import pydantic_settings

dotenv.load_dotenv()

VERSION = "0.0.1"


class Logging(pydantic_settings.BaseSettings, case_sensitive=True):
    """Logging config"""

    LEVEL: str = pydantic.Field(default="DEBUG")
    COLORIZE: bool = pydantic.Field(default=True)
    SERIALIZE: bool = pydantic.Field(default=False)

    model_config = pydantic_settings.SettingsConfigDict(env_prefix="LOGGING_")


class App(pydantic_settings.BaseSettings, case_sensitive=True):
    DEBUG: bool = pydantic.Field(default=False)
    NAME: str = pydantic.Field(default="feeds-api")
    ENV: str = pydantic.Field(default="local")

    model_config = pydantic_settings.SettingsConfigDict(env_prefix="APP_")


class JWT(pydantic_settings.BaseSettings, case_sensitive=False):
    """
    Настройки для локальной проверки access-токенов (без запроса в IAM).
    Должны совпадать с настройками JWT в сервисе IAM.
    """

    secret: str = pydantic.Field(
        default="notset",
        description="Секрет для верификации подписи (тот же что JWT_SECRET в IAM)",
    )
    algorithm: str = pydantic.Field(
        default="HS256",
        description="Алгоритм подписи (HS256 в IAM)",
    )
    issuer: str = pydantic.Field(
        default="kupidon.dev",
        description="Issuer токена (должен совпадать с IAM)",
    )
    audience: str = pydantic.Field(
        default="kupidon-apis",
        description="Audience токена (должен совпадать с IAM)",
    )

    model_config = pydantic_settings.SettingsConfigDict(env_prefix="JWT_")


jwt_settings = JWT()

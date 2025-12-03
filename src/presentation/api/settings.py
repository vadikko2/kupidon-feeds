import dotenv
import pydantic
import pydantic_settings

dotenv.load_dotenv()


class Api(pydantic_settings.BaseSettings):
    max_profiles: int = pydantic.Field(default=100)
    max_requests_per_ip_limit: str = pydantic.Field(default="100/minute")


api_settings = Api()

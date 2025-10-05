import dotenv
import pydantic
import pydantic_settings

dotenv.load_dotenv()


class Api(pydantic_settings.BaseSettings):
    max_profiles: int = pydantic.Field(default=100)


api_settings = Api()

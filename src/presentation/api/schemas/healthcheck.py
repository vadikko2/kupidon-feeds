import pydantic


class Check(pydantic.BaseModel, frozen=True):
    name: pydantic.StrictStr = pydantic.Field(
        description="Check name",
        examples=["redis", "kafka", "postgres"],
    )
    healthy: pydantic.StrictBool = pydantic.Field(default=True)
    error: pydantic.StrictStr = pydantic.Field(
        description="Error message",
        default="",
    )

    def __bool__(self):
        return self.healthy


class Healthcheck(pydantic.BaseModel, frozen=True):
    checks: list[Check] = pydantic.Field(
        description="List of checks",
        default_factory=list,
    )

    @pydantic.computed_field()
    def healthy(self) -> bool:
        return all(self.checks)

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

import cqrs
import pydantic


class DeleteFeed(cqrs.Request):
    account_id: str
    feed_id: pydantic.UUID4

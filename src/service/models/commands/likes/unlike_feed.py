import cqrs
import pydantic


class UnlikeFeed(cqrs.Request):
    feed_id: pydantic.UUID4
    account_id: str

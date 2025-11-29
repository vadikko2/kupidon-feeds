import cqrs
import pydantic


class ViewFeeds(cqrs.Request):
    feed_ids: list[pydantic.UUID4]
    account_id: str


class ViewFeedsResponse(cqrs.Response):
    pass

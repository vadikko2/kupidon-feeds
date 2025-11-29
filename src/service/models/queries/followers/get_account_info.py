import cqrs


class GetAccountInfo(cqrs.Request):
    account_id: str


class GetAccountInfoResponse(cqrs.Response):
    account_id: str
    followers_count: int
    following_count: int
    feeds_count: int

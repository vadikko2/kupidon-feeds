import dataclasses

import cqrs


@dataclasses.dataclass
class GetAccountInfo(cqrs.DCRequest):
    account_id: str


@dataclasses.dataclass
class GetAccountInfoResponse(cqrs.DCResponse):
    account_id: str
    followers_count: int = 0
    following_count: int = 0
    feeds_count: int = 0

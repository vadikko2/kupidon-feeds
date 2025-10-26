from cqrs import events, requests

from service.handlers.commands.feeds import post_feed as post_feed_handler
from service.handlers.commands.images import upload_image as upload_image_handler
from service.handlers.queries.feeds import get_feeds as get_feeds_handler
from service.models.commands import (
    post_feed as post_feed_model,
    upload_image as upload_image_model,
)
from service.models.queries import (
    get_feeds as get_feeds_model,
)


def init_requests(mapper: requests.RequestMap) -> None:
    # commands
    mapper.bind(post_feed_model.PostFeed, post_feed_handler.PostFeedHandler)
    mapper.bind(upload_image_model.UploadImage, upload_image_handler.UploadImageHandler)
    # queries
    mapper.bind(
        get_feeds_model.GetAccountFeeds,
        get_feeds_handler.GetAccountFeedsHandler,
    )


def init_events(mapper: events.EventMap) -> None:
    pass

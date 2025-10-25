from cqrs import events, requests

from service.handlers.commands.feeds import post_feed as post_feed_handler
from service.handlers.commands.images import upload_image as upload_image_handler
from service.models.commands import (
    post_feed as post_feed_model,
    upload_image as upload_image_model,
)


def init_requests(mapper: requests.RequestMap) -> None:
    mapper.bind(post_feed_model.PostFeed, post_feed_handler.PostFeedHandler)
    mapper.bind(upload_image_model.UploadImage, upload_image_handler.UploadImageHandler)


def init_events(mapper: events.EventMap) -> None:
    pass

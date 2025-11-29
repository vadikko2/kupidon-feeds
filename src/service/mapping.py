from cqrs import events, requests

from service.handlers.commands.feeds import (
    delete_feed as delete_feed_handler,
    post_feed as post_feed_handler,
    update_feed as update_feed_handler,
)
from service.handlers.commands.followers import (
    follow as follow_handler,
    unfollow as unfollow_handler,
)
from service.handlers.commands.images import upload_image as upload_image_handler
from service.handlers.commands.likes import (
    like_feed as like_feed_handler,
    unlike_feed as unlike_feed_handler,
)
from service.handlers.commands.views import view_feeds as view_feeds_handler
from service.handlers.queries.feeds import get_feeds as get_feeds_handler
from service.handlers.queries.followers import (
    get_account_info as get_account_info_handler,
    get_followers as get_followers_handler,
    get_following as get_following_handler,
)
from service.handlers.queries.likes import get_likes as get_likes_handler
from service.models.commands.feeds import (
    delete_feed as delete_feed_model,
    post_feed as post_feed_model,
    update_feed as update_feed_model,
)
from service.models.commands.followers import (
    follow as follow_model,
    unfollow as unfollow_model,
)
from service.models.commands.images import upload_image as upload_image_model
from service.models.commands.likes import (
    like_feed as like_feed_model,
    unlike_feed as unlike_feed_model,
)
from service.models.commands.views import view_feeds as view_feeds_model
from service.models.queries.feeds import (
    get_feeds as get_feeds_model,
)
from service.models.queries.followers import (
    get_account_info as get_account_info_model,
    get_followers as get_followers_model,
    get_following as get_following_model,
)
from service.models.queries.likes import get_likes as get_likes_model


def init_requests(mapper: requests.RequestMap) -> None:
    # commands
    mapper.bind(post_feed_model.PostFeed, post_feed_handler.PostFeedHandler)
    mapper.bind(upload_image_model.UploadImage, upload_image_handler.UploadImageHandler)
    mapper.bind(update_feed_model.UpdateFeed, update_feed_handler.UpdateFeedHandler)
    mapper.bind(delete_feed_model.DeleteFeed, delete_feed_handler.DeleteFeedHandler)
    mapper.bind(follow_model.Follow, follow_handler.FollowHandler)
    mapper.bind(unfollow_model.Unfollow, unfollow_handler.UnfollowHandler)
    mapper.bind(like_feed_model.LikeFeed, like_feed_handler.LikeFeedHandler)
    mapper.bind(unlike_feed_model.UnlikeFeed, unlike_feed_handler.UnlikeFeedHandler)
    mapper.bind(view_feeds_model.ViewFeeds, view_feeds_handler.ViewFeedsHandler)
    # queries
    mapper.bind(
        get_feeds_model.GetAccountFeeds,
        get_feeds_handler.GetAccountFeedsHandler,
    )
    mapper.bind(
        get_feeds_model.GetFeeds,
        get_feeds_handler.GetFeedsHandler,
    )
    mapper.bind(
        get_likes_model.GetLikes,
        get_likes_handler.GetLikesHandler,
    )
    mapper.bind(
        get_followers_model.GetFollowers,
        get_followers_handler.GetFollowersHandler,
    )
    mapper.bind(
        get_following_model.GetFollowing,
        get_following_handler.GetFollowingHandler,
    )
    mapper.bind(
        get_account_info_model.GetAccountInfo,
        get_account_info_handler.GetAccountInfoHandler,
    )


def init_events(mapper: events.EventMap) -> None:
    pass

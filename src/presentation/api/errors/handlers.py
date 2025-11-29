from fastapi import status
from fastapi_app.exception_handlers import bind_exception, models
from starlette import requests

from service import exceptions as service_exceptions


@bind_exception(status.HTTP_401_UNAUTHORIZED)
def unauthorized_error_handler(
    _: requests.Request,
    error: service_exceptions.UnauthorizedError,
) -> models.ErrorResponse:
    return models.ErrorResponse(message=str(error))


@bind_exception(status.HTTP_403_FORBIDDEN)
def forbidden_error_handler(
    _: requests.Request,
    error: service_exceptions.GetUserIdError,
) -> models.ErrorResponse:
    return models.ErrorResponse(message=str(error))


@bind_exception(status.HTTP_409_CONFLICT)
def feed_already_exists_error_handler(
    _: requests.Request,
    error: service_exceptions.FeedAlreadyExists,
):
    return models.ErrorResponse(message=str(error))


@bind_exception(status.HTTP_404_NOT_FOUND)
def feed_not_found_error_handler(
    _: requests.Request,
    error: service_exceptions.FeedNotFound,
) -> models.ErrorResponse:
    return models.ErrorResponse(message=str(error))


@bind_exception(status.HTTP_403_FORBIDDEN)
def user_does_not_own_feed_error_handler(
    _: requests.Request,
    error: service_exceptions.UserDoesNotOwnFeed,
) -> models.ErrorResponse:
    return models.ErrorResponse(message=str(error))


@bind_exception(status.HTTP_409_CONFLICT)
def image_already_exists_error_handler(
    _: requests.Request,
    error: service_exceptions.ImageAlreadyExists,
) -> models.ErrorResponse:
    return models.ErrorResponse(message=str(error))


@bind_exception(status.HTTP_404_NOT_FOUND)
def image_not_found_error_handler(
    _: requests.Request,
    error: service_exceptions.ImageNotFound,
) -> models.ErrorResponse:
    return models.ErrorResponse(message=str(error))


@bind_exception(status.HTTP_409_CONFLICT)
def image_already_bound_to_feed_error_handler(
    _: requests.Request,
    error: service_exceptions.ImageAlreadyBoundToFeed,
) -> models.ErrorResponse:
    return models.ErrorResponse(message=str(error))


@bind_exception(status.HTTP_404_NOT_FOUND)
def user_not_found_error_handler(
    _: requests.Request,
    error: service_exceptions.UserNotFound,
) -> models.ErrorResponse:
    return models.ErrorResponse(message=str(error))


@bind_exception(status.HTTP_409_CONFLICT)
def already_following_error_handler(
    _: requests.Request,
    error: service_exceptions.AlreadyFollowing,
) -> models.ErrorResponse:
    return models.ErrorResponse(message=str(error))


@bind_exception(status.HTTP_400_BAD_REQUEST)
def cannot_follow_self_error_handler(
    _: requests.Request,
    error: service_exceptions.CannotFollowSelf,
) -> models.ErrorResponse:
    return models.ErrorResponse(message=str(error))


handlers = [
    unauthorized_error_handler,
    forbidden_error_handler,
    feed_already_exists_error_handler,
    image_already_exists_error_handler,
    image_not_found_error_handler,
    image_already_bound_to_feed_error_handler,
    feed_not_found_error_handler,
    user_does_not_own_feed_error_handler,
    user_not_found_error_handler,
    already_following_error_handler,
    cannot_follow_self_error_handler,
]

import uuid


class UnauthorizedError(Exception):
    def __init__(self, message: str):
        super().__init__(f"Unauthorized: {message}")


class GetUserIdError(Exception):
    def __init__(self, message: str):
        super().__init__(f"Failed to get user ID: {message}")


class FeedAlreadyExists(Exception):
    def __init__(self, feed_id: uuid.UUID):
        super().__init__(f"Feed with id {feed_id} already exists")


class ImageAlreadyExists(Exception):
    def __init__(self, image_id: uuid.UUID):
        super().__init__(f"Image with id {image_id} already exists")


class ImageNotFound(Exception):
    def __init__(self, image_id: uuid.UUID):
        super().__init__(f"Image with id {image_id} not found")


class ImageAlreadyBoundToFeed(Exception):
    def __init__(self, image_id: uuid.UUID, feed_id: uuid.UUID):
        super().__init__(f"Image with id {image_id} already bound to feed {feed_id}")

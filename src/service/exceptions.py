class UnauthorizedError(Exception):
    def __init__(self, message: str):
        super().__init__(f"Unauthorized: {message}")


class GetUserIdError(Exception):
    def __init__(self, message: str):
        super().__init__(f"Failed to get user ID: {message}")

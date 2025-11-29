"""
Factory for creating UoW instances with connection pool support
"""

from infrastructure.persistent import database, unit_of_work


class SQLAlchemyUoWFactory:
    """
    Factory for creating SQLAlchemyUoW instances with connection pool support
    """

    def __init__(self):
        self._session_factory = database.get_session_factory()

    def __call__(self) -> unit_of_work.SQLAlchemyUoW:
        """
        Creates a new UoW instance using the configured session factory
        """
        return unit_of_work.SQLAlchemyUoW(session_factory=self._session_factory)


def create_uow_factory() -> SQLAlchemyUoWFactory:
    """
    Creates a UoW factory instance with connection pool support

    Returns:
        Configured SQLAlchemyUoWFactory instance
    """
    return SQLAlchemyUoWFactory()

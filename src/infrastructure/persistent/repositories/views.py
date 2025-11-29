from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities import view as view_entity
from infrastructure.persistent.orm import ViewORM
from service.interfaces.repositories import views as views_interface


class SQLAlchemyViewsRepository(views_interface.IViewsRepository):
    """
    SQLAlchemy implementation of views repository
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def batch_add(self, views: list[view_entity.View]) -> None:
        """
        Batch add views with idempotency using ON CONFLICT DO NOTHING
        """
        if not views:
            return

        # Prepare data for bulk insert
        values = [
            {
                "feed_id": view.feed_id,
                "account_id": view.account_id,
                "viewed_at": view.viewed_at,
            }
            for view in views
        ]

        # Use PostgreSQL-specific INSERT ... ON CONFLICT DO NOTHING
        # This makes the operation idempotent - duplicate (feed_id, account_id) pairs are ignored
        stmt = (
            pg_insert(ViewORM)
            .values(values)
            .on_conflict_do_nothing(index_elements=["feed_id", "account_id"])
        )

        await self._session.execute(stmt)

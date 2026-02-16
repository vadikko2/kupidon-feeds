from domain.entities import view as view_entity
from infrastructure.persistent.postgres.base import BaseRepository
from service.interfaces.repositories import views as views_interface


class PostgresViewsRepository(BaseRepository, views_interface.IViewsRepository):
    async def batch_add(self, views: list[view_entity.View]) -> None:
        if not views:
            return
        feed_ids = [v.feed_id for v in views]
        account_ids = [v.account_id for v in views]
        viewed_ats = [v.viewed_at for v in views]
        await self.conn.execute(
            """
            INSERT INTO views (feed_id, account_id, viewed_at)
            SELECT * FROM unnest($1::uuid[], $2::text[], $3::timestamptz[])
            ON CONFLICT (feed_id, account_id) DO NOTHING
            """,
            feed_ids,
            account_ids,
            viewed_ats,
        )

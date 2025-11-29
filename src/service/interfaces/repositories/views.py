import abc

from domain.entities import view as view_entity


class IViewsRepository(abc.ABC):
    @abc.abstractmethod
    async def batch_add(self, views: list[view_entity.View]) -> None:
        """
        Batch add views with idempotency (INSERT IGNORE / ON CONFLICT DO NOTHING)
        """
        raise NotImplementedError

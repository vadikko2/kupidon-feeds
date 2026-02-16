"""
Factory for creating UoW instances with asyncpg connection pool.
"""

from __future__ import annotations

import asyncpg

from infrastructure.persistent.postgres import uow as postgres_uow
from service.interfaces import unit_of_work as unit_of_work_interface


class PostgresUoWFactory(unit_of_work_interface.UoWFactory):
    def __init__(self, pool: asyncpg.Pool):
        self._pool = pool

    def __call__(self) -> unit_of_work_interface.UoW:
        return postgres_uow.PostgresUoW(self._pool)

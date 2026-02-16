"""
Postgres (asyncpg) implementation of Unit of Work.
"""

from __future__ import annotations

import typing

import asyncpg
import asyncpg.transaction

from infrastructure.persistent.postgres.repositories import (
    feeds as feeds_repository,
    followers as followers_repository,
    images as images_repository,
    likes as likes_repository,
    views as views_repository,
)
from service.interfaces import unit_of_work as unit_of_work_interface


class PostgresUoW(unit_of_work_interface.UoW):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
        self._conn: asyncpg.Connection | None = None
        self._transaction: asyncpg.transaction.Transaction | None = None
        self._committed: bool = False
        self._entered: bool = False
        self._closed: bool = False

    async def __aenter__(self) -> typing.Self:
        if self._entered:
            raise RuntimeError("PostgresUoW context manager cannot be entered twice")
        if self._closed:
            raise RuntimeError(
                "PostgresUoW has already been closed and cannot be reused",
            )

        self._entered = True
        try:
            self._conn = await self.pool.acquire()
            assert self._conn is not None
            self._transaction = self._conn.transaction()
            assert self._transaction is not None
            await self._transaction.start()
            self._committed = False

            self.feeds_repository = feeds_repository.PostgresFeedsRepository(self._conn)
            self.images_repository = images_repository.PostgresImagesRepository(
                self._conn,
            )
            self.followers_repository = (
                followers_repository.PostgresFollowersRepository(
                    self._conn,
                )
            )
            self.likes_repository = likes_repository.PostgresLikesRepository(self._conn)
            self.views_repository = views_repository.PostgresViewsRepository(
                self._conn,
            )

            return self
        except Exception:
            self._entered = False
            if self._conn:
                await self.pool.release(self._conn)
                self._conn = None
            raise

    async def commit(self) -> None:
        if not self._entered:
            raise RuntimeError("Cannot commit: UoW context manager not entered")
        if self._closed:
            raise RuntimeError("Cannot commit: UoW has already been closed")
        if self._transaction and not self._committed:
            await self._transaction.commit()
            self._committed = True

    async def rollback(self) -> None:
        if not self._entered:
            raise RuntimeError("Cannot rollback: UoW context manager not entered")
        if self._closed:
            raise RuntimeError("Cannot rollback: UoW has already been closed")
        if self._transaction and not self._committed:
            await self._transaction.rollback()
            self._committed = True

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            if not self._entered:
                return

            if exc_type:
                await self.rollback()
            elif self._transaction and not self._committed:
                await self.commit()
        finally:
            if self._conn:
                await self.pool.release(self._conn)
                self._conn = None
                self._transaction = None
                self._committed = False
                self._entered = False
                self._closed = True

import asyncpg


class BaseRepository:
    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn

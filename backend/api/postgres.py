import contextlib
import os
import typing as t
from pathlib import Path

import asyncpg  # type: ignore
from pydantic import BaseSettings, validator

Connection = asyncpg.Connection


class PostgresConfig(BaseSettings):
    database: str
    user: str
    password: t.Optional[str]
    host: str
    port: int
    migrations_dir: Path

    # pylint: disable=no-self-argument,no-self-use
    @validator("host")
    def unix_socket_absolute_path(cls, host: str) -> str:
        # Resolve relative paths to the project root since asyncpg
        # expects an absolute path if we're connecting on a Unix socket.
        if host.startswith("./"):
            project_root = Path(os.environ["PROJECT_ROOT"])
            return str((project_root / host).resolve())
        return host

    class Config:
        env_prefix = "postgres_"


async def initialize_pool(postgres: PostgresConfig) -> asyncpg.Pool:
    return await asyncpg.create_pool(
        host=postgres.host,
        port=postgres.port,
        user=postgres.user,
        password=postgres.password,
        database=postgres.database,
        server_settings={"application_name": "api"},
    )


async def connect_and_migrate(postgres: PostgresConfig) -> None:
    migrations = [
        migration.read_text()
        for migration in postgres.migrations_dir.iterdir()
        if migration.suffix == ".sql"
    ]

    await Postgres.connect(postgres)
    async with contextlib.asynccontextmanager(Postgres.connection)() as conn:
        for migration in migrations:
            await conn.execute(migration)


# FastAPI dependency for database connections. Saves the given pool
# into a class variable to avoid initializing it into a global at
# import time. Provides `connection`
class Postgres:
    _pool: asyncpg.Pool = None

    def __init__(self) -> None:
        assert Postgres._pool is not None

    # Call this with `contextlib.asynccontextmanager` to use directly.
    # FastAPI needs the generator version for `Depends()`
    @staticmethod
    async def connection() -> t.AsyncGenerator[asyncpg.Connection, None]:
        assert Postgres._pool is not None
        async with Postgres._pool.acquire() as conn:
            yield conn

    @staticmethod
    async def connect(postgres: PostgresConfig) -> None:
        assert Postgres._pool is None
        Postgres._pool = await initialize_pool(postgres)

    @staticmethod
    async def disconnect() -> None:
        assert Postgres._pool is not None
        await Postgres._pool.close()

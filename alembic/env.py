import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from app.config import settings
from app.models.base import Base

target_metadata = Base.metadata

# 設定 target_metadata 的 schema
target_metadata.schema = settings.db_schema


def include_object(object, name, type_, reflected, compare_to):
    """
    過濾函數，只包含指定 schema 的對象
    """
    # 對於表對象的處理
    if type_ == "table":
        # 如果是從資料庫反射的表
        if reflected:
            # 只包含目標 schema 的表
            return hasattr(object, "schema") and object.schema == settings.db_schema
        else:
            # 如果是我們模型定義的表，檢查其 schema
            return hasattr(object, "schema") and object.schema == settings.db_schema
    
    # 對於索引、外鍵等其他對象
    if type_ in ("index", "foreign_key_constraint", "unique_constraint", "check_constraint"):
        # 檢查關聯的表是否在目標 schema 中
        if hasattr(object, "table") and hasattr(object.table, "schema"):
            return object.table.schema == settings.db_schema
    
    # 對於其他類型的對象，使用預設行為
    return True


def include_name(name, type_, parent_names):
    """
    過濾名稱，只包含我們關心的對象
    """
    # 對於 schema 名稱的過濾
    if type_ == "schema":
        return name == settings.db_schema
    
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,  # 允許包含 schema
        include_object=include_object,
        include_name=include_name,
        version_table_schema=settings.db_schema,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_schemas=True,  # 允許包含 schema
        include_object=include_object,
        include_name=include_name,
        version_table_schema=settings.db_schema,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

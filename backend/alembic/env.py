import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context

# 🔹 Importa a configuração correta do banco e os modelos
from app.database import sync_engine  # Agora Alembic usa a engine síncrona
from app.models import Base  # Agora Alembic sabe onde encontrar os modelos do banco

# Configuração de logging do Alembic
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Define os metadados para autogenerate funcionar corretamente
target_metadata = Base.metadata

def run_migrations_offline():
    """Executa as migrações em modo offline."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Executa as migrações em modo online."""
    connectable = sync_engine  # 🔹 Agora Alembic usa a engine síncrona para evitar erros

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

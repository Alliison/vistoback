from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente do .env
load_dotenv()

# Configuração do banco de dados PostgreSQL via .env
DATABASE_URL = os.getenv("DATABASE_URL")

# 🔹 Criando a conexão assíncrona para FastAPI
async_engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# 🔹 Criando a conexão síncrona para Alembic
SYNC_DATABASE_URL = DATABASE_URL.replace("asyncpg", "psycopg2")
sync_engine = create_engine(SYNC_DATABASE_URL, echo=False, future=True)

# 🔹 Criando sessão assíncrona para FastAPI
AsyncSessionLocal = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

# Criando a base do ORM
Base = declarative_base()

# 🔹 Dependência do banco para FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

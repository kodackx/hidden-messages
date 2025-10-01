from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback to local SQLite file when not provided (dev/no-docker)
if not DATABASE_URL:
    DATABASE_URL = "sqlite+aiosqlite:///./hidden_messages_dev.db"

# Normalize/derive async URL
if DATABASE_URL.startswith("postgresql+psycopg://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg://", "postgresql+asyncpg://")
elif DATABASE_URL.startswith("postgresql+asyncpg://"):
    ASYNC_DATABASE_URL = DATABASE_URL
elif DATABASE_URL.startswith("sqlite+aiosqlite://"):
    ASYNC_DATABASE_URL = DATABASE_URL
elif DATABASE_URL.startswith("sqlite://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
else:
    # Unknown scheme → safe dev fallback
    ASYNC_DATABASE_URL = "sqlite+aiosqlite:///./hidden_messages_dev.db"

Base = declarative_base()

# Set echo=False to reduce SQL query logging (can be enabled via env var for debugging)
echo_sql = os.getenv("SQL_ECHO", "false").lower() == "true"
engine = create_async_engine(ASYNC_DATABASE_URL, echo=echo_sql)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

Session = SessionLocal
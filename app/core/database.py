from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import config

async_engine = create_async_engine(
    config.database.async_dsn,
    echo=False,
    pool_size=30,
    max_overflow=20,
    pool_timeout=60,
    pool_recycle=1800,
)

AsyncSessionFactory = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


<<<<<<< HEAD
=======
# Dependency: yields a fully async DB session with commit/rollback
>>>>>>> 1e6f4b61bd2dc388852b3f1b09697b0a276db0c0
async def get_db() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise


<<<<<<< HEAD
=======
# Optional aliases
>>>>>>> 1e6f4b61bd2dc388852b3f1b09697b0a276db0c0
get_async_session = get_db
get_async_db = get_db

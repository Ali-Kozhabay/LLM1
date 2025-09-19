from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker, AsyncSession

from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL1)
SessionLocal = async_sessionmaker(autocommit=False, class_=AsyncSession, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with SessionLocal() as db:
        yield db
 
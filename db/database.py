from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL="postgresql+asyncpg://postgres:Admin@localhost:5432/Doctor_appointment1_bot"
class Base(DeclarativeBase):
    pass

engine=create_async_engine(DATABASE_URL,echo=True)
async_session_maker = async_sessionmaker(engine,expire_on_commit=False,class_=AsyncSession)
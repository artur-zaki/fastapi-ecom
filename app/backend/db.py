from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

import os
from dotenv import load_dotenv

load_dotenv()

POSTGRESQL_ECOM_PASSWORD = os.getenv("POSTGRESQL_ECOM_PASSWORD")
url = f'postgresql+asyncpg://ecommerce:{POSTGRESQL_ECOM_PASSWORD}@localhost:5432/ecommerce'

engine = create_async_engine(url, echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass
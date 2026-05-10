from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import MetaData, create_engine

from globals import DB_URL

async_engine = create_async_engine(DB_URL, echo=False)
sync_engine = create_engine(DB_URL, echo=False)
async_session_maker = async_sessionmaker(bind=async_engine, expire_on_commit=False)
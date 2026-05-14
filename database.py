from sqlalchemy import select

from db_engine import async_session_maker
from models import UserModel

async def get_user(user_id: int):
    async with async_session_maker() as session:
        stmt = (
            select(UserModel)
            .where(UserModel.id==user_id)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    

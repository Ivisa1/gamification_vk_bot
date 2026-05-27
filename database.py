from sqlalchemy import select, and_

from bot import tasks_list_params
from db_engine import async_session_maker
from models import UserModel, TasksModel

async def get_user(user_id: int):
    async with async_session_maker() as session:
        stmt = (
            select(UserModel)
            .where(UserModel.id==user_id)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
async def get_task(user_id: int) -> TasksModel:
    async with async_session_maker() as session:
        stmt = (
            select(TasksModel)
            .where(
                and_(
                    TasksModel.user_id==user_id,
                    TasksModel.type.in_(tasks_list_params[user_id]['types']),
                    TasksModel.difficulty.in_(tasks_list_params[user_id]['difficulties'])
                )
            )
            .order_by(TasksModel.id.asc())
            .limit(1)
            .offset(tasks_list_params[user_id]['curr_offset'])
        )
        result = await session.execute(stmt)
        task: TasksModel = result.scalar()
        return task
